import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'dart:io';
import 'package:webview_flutter_android/webview_flutter_android.dart';
import 'package:file_picker/file_picker.dart';
import 'package:cross_file/cross_file.dart';
import 'package:flutter/services.dart';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:open_filex/open_filex.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:package_info_plus/package_info_plus.dart';
import 'package:url_launcher/url_launcher.dart';

class OnionWebView extends StatefulWidget {

  const OnionWebView({super.key});


  @override
  State<OnionWebView> createState() => _OnionWebViewState();

}



class _OnionWebViewState extends State<OnionWebView> {

  final ValueNotifier<double> downloadProgress = ValueNotifier(0.0);
  bool isDownloading = false;

  late WebViewController controller;

  static const platform = MethodChannel('tor_channel');

  String? selectedFile;

  bool torLoading = true;

  final String onionSite =
      "6oursdthkgh6bpa3e37hm4jojhpinizbjr7ntdjaabmehhpesu54bcqd.onion";


   Future<void> openUpdatePage() async {
     final url = Uri.parse(
       "https://tasib-dev.github.io/cloud-storage-update/",
     );

     final ok = await launchUrl(
       url,
       mode: LaunchMode.externalApplication,
     );

     if (!ok && mounted) {
       ScaffoldMessenger.of(context).showSnackBar(
         const SnackBar(
           content: Text("Could not open update page."),
         ),
       );
     }
   }

   void showDownloadDialog() {
     showDialog(
       context: context,
       barrierDismissible: false,
       builder: (context) {
         return AlertDialog(
           title: const Text("Downloading Update"),
           content: ValueListenableBuilder<double>(
             valueListenable: downloadProgress,
             builder: (context, progress, child) {
               return Column(
                 mainAxisSize: MainAxisSize.min,
                 children: [
                   LinearProgressIndicator(value: progress),
                   const SizedBox(height: 12),
                   Text("${(progress * 100).toStringAsFixed(0)}%"),
                 ],
               );
             },
           ),
         );
       },
     );
   }

  Future<void> downloadFile(String url) async {
    print("STEP 1");

    try {
      final dir = await getTemporaryDirectory();
      print("STEP 2");
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(dir.path),
          duration: const Duration(seconds: 8),
        ),
      );

      final fileName = url.split('/').last;
      final savePath = "${dir.path}/$fileName";

      print("Save path: $savePath");

      final dio = Dio();

      print("STEP 3");

      setState(() {
        isDownloading = true;
      });

      downloadProgress.value = 0.0;


      await dio.download(
        url,
        savePath,
        onReceiveProgress: (received, total) {
          print("received=$received total=$total");

          if (total > 0) {
            downloadProgress.value = received / total;

            print(
              "Progress: ${(downloadProgress.value * 100).toStringAsFixed(0)}%",
            );
          }
        },
      );

      setState(() {
        isDownloading = false;
      });

      print("STEP 4");

      final file = File(savePath);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            "Exists: ${await file.exists()}  Size: ${await file.length()}",
          ),
          duration: const Duration(seconds: 6),
        ),
      );

      print("Exists: ${await file.exists()}");
      print("Size: ${await file.length()}");

      final bytes = await file.openRead(0, 8).first;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(bytes.toString()),
          duration: const Duration(seconds: 8),
        ),
      );

      try {
        await platform.invokeMethod(
          "installApk",
          {
            "path": savePath,
          },
        );
      } on PlatformException catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Install error: ${e.message}"),
            duration: const Duration(seconds: 8),
          ),
        );
      }





    } catch (e, stack) {
      print("ERROR:");
      print(e);
      print(stack);
    }
  }


Future<void> showUpdateDialog({
  required String latestVersion,
  required bool force,
  required String message,
  required String apkUrl,
}) async {

  await showDialog(
    context: context,
    barrierDismissible: !force,

    builder: (context) {

      return AlertDialog(

        title: const Text("Update Available"),

        content: Text(
          "Version $latestVersion\n\n$message",
        ),

        actions: [

          if (!force)
            TextButton(

              onPressed: () {

                Navigator.pop(context);

              },

              child: const Text("Later"),

            ),

          ElevatedButton(

            onPressed: () async {

              Navigator.pop(context);

              await openUpdatePage();

            },

            child: const Text("Update"),

          ),

        ],

      );

    },

  );

}

  Future<void> checkForUpdate() async {

    try {

      final packageInfo = await PackageInfo.fromPlatform();

      final installedVersion = packageInfo.version;
      final installedBuild = int.parse(packageInfo.buildNumber);

      print("Installed version: $installedVersion");
      print("Installed build: $installedBuild");

      final response = await http.get(
        Uri.parse(
          "https://tasib-dev.github.io/cloud-storage-update/version.json",
        ),
      );

      print("Status Code: ${response.statusCode}");

      final data = jsonDecode(response.body);

      final latestVersion = data["version"];
      final latestBuild = int.parse(data["build"].toString());
      final force = data["force"];
      final message = data["message"];
      final apk = data["apk"];

      print("Latest version: $latestVersion");
      print("Latest build: $latestBuild");
      print("Force update: $force");
      print("Message: $message");

      if (installedBuild >= latestBuild) {

        print("App is already up to date.");

      } else {

        await showUpdateDialog(
          latestVersion: latestVersion,
          force: force,
          message: message,
          apkUrl: apk,
        );

      }

    } catch (e, stack) {
      print("========== UPDATE ERROR ==========");
      print(e);
      print(stack);
    }

  }


  @override
  void initState() {

    super.initState();


    controller = WebViewController.fromPlatformCreationParams(
      const PlatformWebViewControllerCreationParams(),
    );

    if (Platform.isAndroid) {
      AndroidWebViewController.enableDebugging(true);
    }


    controller

      ..setJavaScriptMode(
        JavaScriptMode.unrestricted
      )


      ..setNavigationDelegate(
        NavigationDelegate(

          onPageStarted: (url) {
            print("PAGE STARTED: $url");
          },


          onPageFinished: (url) {
            print("PAGE FINISHED: $url");
          },


          onNavigationRequest: (request) async {

            print("URL: ${request.url}");

            if (request.url.contains("/download/")) {

              print("DOWNLOAD DETECTED");

              await downloadFile(request.url);

              return NavigationDecision.prevent;
            }

            return NavigationDecision.navigate;
          },

        ),
      );






    if (Platform.isAndroid) {

      final androidController =
          controller.platform as AndroidWebViewController;

          androidController.setOnPlatformPermissionRequest(
            (request) {
              request.grant();
            },
          );


      androidController.setJavaScriptMode(JavaScriptMode.unrestricted);



      androidController.setOnShowFileSelector(
        (params) async {

          final result = await FilePicker.platform.pickFiles(
            allowMultiple: false,
            withData: false,
          );

          if (result != null && result.files.single.path != null) {

            final file = File(result.files.single.path!);

            print("SELECTED FILE: ${file.path}");

            final size = await file.length();

            print("SIZE: $size bytes");

            return [
              file.uri.toString()
            ];

          }

          return [];
        },
      );

    }
    startTorAndLoad();

  }

  Future<void> startTorAndLoad() async {

    try {

      await platform.invokeMethod("startTor");

      print("Tor start requested");


      bool ready = false;


      while(!ready){

        try {

          final result =
              await platform.invokeMethod("testTor");


          print(result);

          ready = true;


        } catch(e){

          print("Waiting for Tor...");

          await Future.delayed(
            const Duration(seconds: 2)
          );

        }

      }


      print("Tor is ready");

      await checkForUpdate();


      setState(() {
        torLoading = false;
      });


      controller.loadRequest(
        Uri.parse(
          "http://127.0.0.1:8080/$onionSite/"
        )
      );


    } catch(e){

      print("TOR ERROR: $e");

    }

  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      appBar: AppBar(
        title: const Text("Vault Nest"),
      ),


      body: torLoading
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [

                  CircularProgressIndicator(),

                  SizedBox(height: 20),

                  Text(
                    "Starting Tor..."
                  ),

                ],
              ),
            )

          : Column(
              children: [
                Expanded(
                  child: WebViewWidget(
                    controller: controller,
                  ),
                ),

              ],
            ),

    );

  }

}