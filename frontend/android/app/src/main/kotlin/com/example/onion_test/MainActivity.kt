package com.example.onion_test

import android.content.ComponentName
import android.content.Intent
import android.content.ServiceConnection
import android.os.Bundle
import android.os.IBinder
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import org.torproject.jni.TorService
import java.net.HttpURLConnection
import java.net.InetSocketAddress
import java.net.Proxy
import java.net.URL
import kotlin.concurrent.thread
import java.net.URLEncoder
import android.util.Log
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.net.Uri
import android.content.ActivityNotFoundException
import androidx.core.content.FileProvider
import android.content.pm.PackageManager
import java.io.File


class MainActivity : FlutterActivity() {

    private var bridge: TorHttpBridge? = null
    private val CHANNEL = "tor_channel"

    private var filePathCallback: ValueCallback<Array<Uri>>? = null

    private val FILE_PICKER = 100

    private var torService: TorService? = null

    private val connection = object : ServiceConnection {

        override fun onServiceConnected(
            name: ComponentName?,
            service: IBinder?
        ) {

            torService = (service as TorService.LocalBinder).service

        }

        override fun onServiceDisconnected(name: ComponentName?) {
            torService = null
        }
    }


    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)


        MethodChannel(
            flutterEngine.dartExecutor.binaryMessenger,
            CHANNEL
        ).setMethodCallHandler { call, result ->


            when(call.method) {


                "startTor" -> {

                    Log.d("TORTEST", "Before bindService")

                    val intent =
                        Intent(this, TorService::class.java)


                    bindService(
                        intent,
                        connection,
                        BIND_AUTO_CREATE
                    )

                    Log.d("TORTEST", "After bindService")


                    // Start local HTTP bridge
                    if (bridge == null) {

                        Log.d("TORTEST", "Starting bridge")

                        bridge = TorHttpBridge()

                        bridge?.start()

                        Log.d("TORTEST", "Bridge started")
                    }


                    result.success("Tor service started")
                }



                "testTor" -> {

                    thread {

                        try {

                            val proxy = Proxy(
                                Proxy.Type.SOCKS,
                                InetSocketAddress(
                                    "127.0.0.1",
                                    9050
                                )
                            )


                            val url = URL(
                                "https://check.torproject.org/api/ip"
                            )


                            val connection =
                                url.openConnection(proxy)
                                        as HttpURLConnection


                            connection.connectTimeout = 15000
                            connection.readTimeout = 15000


                            val response =
                                connection.inputStream
                                    .bufferedReader()
                                    .readText()


                            runOnUiThread {

                                result.success(response)

                            }


                        } catch(e: Exception) {


                            runOnUiThread {

                                result.error(
                                    "TOR_ERROR",
                                    e.toString(),
                                    null
                                )

                            }

                        }

                    }

                }

                "testOnion" -> {

                    thread {

                        try {


                            val url = URL(
                                "http://127.0.0.1:8080/mjyvi3j665q5ekika4s6qrdwfxpgbn4hu4izxjnlw6jdz2cqonmjgayd.onion"
                            )


                            val connection =
                                url.openConnection( )
                                        as HttpURLConnection


                            connection.connectTimeout = 30000
                            connection.readTimeout = 30000


                            val response =
                                connection.inputStream
                                    .bufferedReader()
                                    .readText()



                            runOnUiThread {

                                result.success(response)

                            }


                        } catch(e: Exception) {


                            runOnUiThread {

                                result.error(
                                    "ONION_ERROR",
                                    e.toString(),
                                    null
                                )

                            }

                        }

                    }

                }

                "installApk" -> {

                    val path = call.argument<String>("path")

                    if (path == null) {
                        result.error("ERROR", "Path is null", null)
                        return@setMethodCallHandler
                    }

                    val file = File(path)

                    val uri = FileProvider.getUriForFile(
                        this,
                        packageName + ".fileprovider",
                        file
                    )

                    val intent = Intent(Intent.ACTION_VIEW).apply {
                        setDataAndType(
                            uri,
                            "application/vnd.android.package-archive"
                        )
                        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    }



                    try {
                        startActivity(intent)
                        result.success("OK")
                    } catch (e: Exception) {
                        result.error("INSTALL_ERROR", e.toString(), null)
                    }
                }




                else -> result.notImplemented()

            }

        }

    }

    override fun onActivityResult(
        requestCode: Int,
        resultCode: Int,
        data: Intent?
    ) {
        super.onActivityResult(requestCode, resultCode, data)

        if (requestCode == FILE_PICKER) {

            val result =
                if (data?.data != null)
                    arrayOf(data.data!!)
                else
                    null

            filePathCallback?.onReceiveValue(result)

            filePathCallback = null
        }
    }



}