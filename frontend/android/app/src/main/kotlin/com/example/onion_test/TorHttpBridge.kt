package com.example.onion_test

import fi.iki.elonen.NanoHTTPD
import java.net.*
import android.util.Log


class TorHttpBridge : NanoHTTPD(8080) {

    @Volatile
    private var uploadTotal: Long = 0

    @Volatile
    private var uploadSent: Long = 0

    @Volatile
    private var uploadActive = false


    private val onionHost =
        "6oursdthkgh6bpa3e37hm4jojhpinizbjr7ntdjaabmehhpesu54bcqd.onion"

    @Volatile
    private var savedCookie: String? = null





    override fun serve(session: IHTTPSession): Response {

        println("BRIDGE RECEIVED URI = ${session.uri}")

        if (session.uri == "/upload-progress") {

            val percent =
                if (uploadTotal == 0L)
                    0
                else
                    ((uploadSent * 100) / uploadTotal).toInt()

            val json = """
            {
                "active": $uploadActive,
                "sent": $uploadSent,
                "total": $uploadTotal,
                "percent": $percent
            }
        """.trimIndent()

            return newFixedLengthResponse(
                Response.Status.OK,
                "application/json",
                json
            )
        }


        try {


            val targetUrl =
                if (session.uri.contains(onionHost)) {

                    "http://${session.uri.removePrefix("/")}"

                } else {

                    "http://$onionHost${session.uri}"

                }



            println("TARGET = $targetUrl")
            println("METHOD = ${session.method}")



            val proxy = Proxy(
                Proxy.Type.SOCKS,
                InetSocketAddress(
                    "127.0.0.1",
                    9050
                )
            )



            val connection =
                URL(targetUrl)
                    .openConnection(proxy)
                        as HttpURLConnection

            connection.instanceFollowRedirects = false



            connection.requestMethod =
                session.method.name



            // Get cookie from the current request
            var clientCookie = session.headers["cookie"]

// If this request has a cookie, remember it
            if (clientCookie != null) {
                savedCookie = clientCookie
            }
// Otherwise, reuse the last known cookie
            else {
                clientCookie = savedCookie
            }

            println("COOKIES USED = $clientCookie")

            if (clientCookie != null) {
                connection.setRequestProperty(
                    "Cookie",
                    clientCookie
                )
            }



            connection.instanceFollowRedirects = false

            connection.connectTimeout = 60000
            connection.readTimeout = 60000



            // Forward POST body
            if(session.method == Method.POST){


                val contentLength =
                    session.headers["content-length"]
                        ?.toInt()
                        ?: 0



                val buffer = ByteArray(contentLength)

                var totalRead = 0

                while (totalRead < contentLength) {
                    val bytesRead = session.inputStream.read(
                        buffer,
                        totalRead,
                        contentLength - totalRead
                    )

                    if (bytesRead == -1) {
                        break
                    }

                    totalRead += bytesRead
                }

                println("Expected: $contentLength")
                println("Actually read: $totalRead")



                connection.doOutput = true

                uploadTotal = totalRead.toLong()
                uploadSent = 0
                uploadActive = true



                connection.setRequestProperty(
                    "Content-Type",
                    session.headers["content-type"]
                        ?: "application/x-www-form-urlencoded"
                )



                connection.outputStream.use { out ->

                    val chunkSize = 8192
                    var offset = 0

                    while (offset < totalRead) {

                        val bytesToWrite = minOf(chunkSize, totalRead - offset)

                        out.write(buffer, offset, bytesToWrite)

                        uploadSent += bytesToWrite

                        Log.d("TorUpload", "UPLOAD: $uploadSent / $uploadTotal")

                        offset += bytesToWrite
                    }

                    out.flush()
                }

            }


            println("REQUEST TARGET = ${session.uri}")
            println("FULL TARGET URL = $targetUrl")
            println("STATUS = ${connection.responseCode}")
            println("LOCATION = ${connection.getHeaderField("Location")}")

            val response =
                if (connection.responseCode in 300..399) {

                    val location = connection.getHeaderField("Location")

                    val redirectUrl =
                        if (location != null && location.startsWith("/")) {
                            "http://127.0.0.1:8080$location"
                        } else {
                            location ?: "http://127.0.0.1:8080/"
                        }

                    newFixedLengthResponse(
                        Response.Status.REDIRECT,
                        "text/plain",
                        ""
                    ).apply {

                        addHeader(
                            "Location",
                            redirectUrl
                        )

                    }

                } else {

                    newFixedLengthResponse(
                        Response.Status.OK,
                        connection.contentType ?: "text/html",
                        connection.inputStream,
                        connection.contentLengthLong
                    )

                }





            // Forward Flask cookies to WebView
            val cookies =
                connection.headerFields["Set-Cookie"]


            if(cookies != null){

                for(cookie in cookies){

                    response.addHeader(
                        "Set-Cookie",
                        cookie
                    )

                }

            }



            return response



        } catch(e: Exception){


            e.printStackTrace()


            return newFixedLengthResponse(
                Response.Status.INTERNAL_ERROR,
                "text/plain",
                e.toString()
            )

        }

    }

}