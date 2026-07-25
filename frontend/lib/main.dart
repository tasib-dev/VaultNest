import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'onion_webview.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}



class MyApp extends StatelessWidget {

  const MyApp({super.key});




  static const channel =
      MethodChannel('tor_channel');





  @override
  Widget build(BuildContext context) {

    return MaterialApp(

      home: OnionPage(),

    );

  }

}






class OnionPage extends StatefulWidget {

  const OnionPage({super.key});


  @override
  State<OnionPage> createState() =>
      _OnionPageState();

}






class _OnionPageState extends State<OnionPage> {



  String html =
      "Press Start Tor first";





  static const channel =
      MethodChannel('tor_channel');


  Future<void> getAppVersion() async {

    PackageInfo packageInfo = await PackageInfo.fromPlatform();

    print("Version: ${packageInfo.version}");
    print("Build: ${packageInfo.buildNumber}");

  }



  @override
    void initState() {
      super.initState();

      getAppVersion();

    }




  Future<void> startTor() async {


    try {


      final result =
          await channel.invokeMethod("startTor");


      print(result);


      setState(() {

        html = "Tor started. Wait a few seconds then press Open Onion";

      });



    } catch(e) {


      setState(() {

        html = e.toString();

      });


    }


  }







  Future<void> loadOnion() async {


    try {


      final result =
          await channel.invokeMethod("testOnion");



      setState(() {


        html = result.toString();


      });



    }

    catch(e){


      setState(() {


        html = e.toString();


      });


    }


  }








  @override
  Widget build(BuildContext context) {


    return Scaffold(


      appBar: AppBar(

        title:
        const Text("Onion Test"),

      ),





      body: Column(


        children: [



          ElevatedButton(


            onPressed: startTor,


            child:
            const Text("Start Tor"),


          ),




          ElevatedButton(
            onPressed: () {

              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const OnionWebView(),
                ),
              );

            },
            child: const Text("Open Onion"),
          ),





          Expanded(


            child: SingleChildScrollView(


              padding:
              const EdgeInsets.all(20),



              child:
              Text(html),


            ),


          )



        ],


      ),


    );


  }


}

