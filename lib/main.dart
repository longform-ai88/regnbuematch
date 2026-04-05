import 'dart:convert';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

const String BASE_URL = "http://192.168.1.185:8000";

Future<String> sendToAI(String prompt) async {
  final response = await http.post(
    Uri.parse('http://127.0.0.1:8000/ai'),
    headers: {"Content-Type": "application/json"},
    body: jsonEncode({"prompt": prompt}),
  );

  final data = jsonDecode(response.body);
  return data["result"];
}

List users = [
  {"name": "Alex", "age": 24, "image": "https://i.pravatar.cc/300?img=1"},
  {"name": "Sam", "age": 27, "image": "https://i.pravatar.cc/300?img=2"},
  {"name": "Lina", "age": 22, "image": "https://i.pravatar.cc/300?img=3"},
];

void main() {
  runApp(RegnbueMatchApp());
}

class RegnbueMatchApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  double x = 100;
  double y = 200;
  int currentIndex = 0;
  List likedUsers = [];
  String result = "";

  @override
  void initState() {
    super.initState();
    x = 0;
    y = 0;
  }

  void handleAI() async {
    String res = await sendToAI("Lag en kul dating bio");

    setState(() {
      result = res;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.pink[50],
      appBar: AppBar(
        title: Text("Regnbuematch 🌈"),
        centerTitle: true,
        backgroundColor: Colors.pink,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: handleAI,
              child: Text("Test AI"),
            ),
            SizedBox(height: 20),
            Container(
              padding: EdgeInsets.all(20),
              margin: EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(color: Colors.black12, blurRadius: 10)
                ],
              ),
              child: Text(
                result,
                style: TextStyle(fontSize: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget buildDraggableCard() {
    if (currentIndex >= users.length) {
      final matches = likedUsers.map((user) => user['name'] as String).toList();

      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("No more users"),
            SizedBox(height: 20),
            Text("Matches:", style: TextStyle(fontSize: 20)),
            Column(
              children: matches.map((name) {
                return GestureDetector(
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => ChatPage(name: name),
                      ),
                    );
                  },
                  child: Padding(
                    padding: EdgeInsets.all(8),
                    child: Text(
                      name,
                      style: TextStyle(fontSize: 18, color: Colors.blue),
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ),
      );
    }

    return AnimatedPositioned(
      duration: Duration(milliseconds: 500),
      left: MediaQuery.of(context).size.width / 2 - 150 + x,
      top: MediaQuery.of(context).size.height / 2 - 200 + y,
      child: Transform(
        transform: Matrix4.rotationZ(x / 300),
        child: GestureDetector(
          onPanUpdate: (details) {
            setState(() {
              x += details.delta.dx;
              y = 0;
            });
          },
          onPanEnd: (details) {
            if (x > 100) {
              print("LIKE 👍");

              likedUsers.add(users[currentIndex]);

              setState(() {
                currentIndex++;
                x = 0;
                y = 0;
              });
            } else if (x < -100) {
              print("NOPE ❌");

              setState(() {
                currentIndex++;
                x = 0;
                y = 0;
              });
            } else {
              setState(() {
                x = 0;
                y = 0;
              });
            }
          },
          child: Stack(
            children: [
              buildCard(),
              if (x > 20)
                Positioned(
                  top: 50,
                  left: 20,
                  child: Opacity(
                    opacity: (x.abs() / 100).clamp(0, 1),
                    child: Text(
                      "LIKE 👍",
                      style: TextStyle(
                        fontSize: 32,
                        color: Colors.green,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              if (x < -20)
                Positioned(
                  top: 50,
                  right: 20,
                  child: Opacity(
                    opacity: (x.abs() / 100).clamp(0, 1),
                    child: Text(
                      "NOPE ❌",
                      style: TextStyle(
                        fontSize: 32,
                        color: Colors.red,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget buildCard() {
    if (currentIndex >= users.length) {
      return SizedBox.shrink();
    }

    final user = users[currentIndex];

    return Card(
      elevation: 10,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      child: Center(
        child: buildCardContent(user),
      ),
    );
  }

  Widget buildCardAt(int index, {double scale = 1}) {
    final user = users[index];

    return Transform.scale(
      scale: scale,
      child: Card(
        elevation: 10,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        child: Center(
          child: buildCardContent(user),
        ),
      ),
    );
  }

  Widget buildCardContent(dynamic user) {
    return Container(
      width: 300,
      height: 400,
      padding: EdgeInsets.all(16),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircleAvatar(
            radius: 50,
            backgroundImage: NetworkImage(
              user['image'] ?? "https://i.pravatar.cc/300?img=1",
            ),
          ),
          SizedBox(height: 20),
          Text(
            "${user['name'] ?? 'Unknown'}, ${user['age'] ?? 'N/A'}",
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 10),
          Text("Oslo 🌍"),
        ],
      ),
    );
  }
}

class ChatPage extends StatefulWidget {
  final String name;

  ChatPage({required this.name});

  @override
  _ChatPageState createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  ScrollController scrollController = ScrollController();
  List<Map<String, dynamic>> messages = [];
  TextEditingController controller = TextEditingController();

  void sendMessage() async {
    if (controller.text.isEmpty) return;

    String userText = controller.text;

    setState(() {
      messages.add({
        "text": userText,
        "isMe": true,
      });
      messages.add({
        "text": "Alex skriver...",
        "isTyping": true,
        "isMe": false,
      });
    });

    controller.clear();

    scrollController.animateTo(
      0,
      duration: Duration(milliseconds: 300),
      curve: Curves.easeOut,
    );

    autoReply(userText); // 👈 viktig
  }

  String getAIResponse() {
    List<String> replies = [
      "Hei 😊",
      "Hva skjer?",
      "Haha 😄",
      "Fortell mer 👀",
      "Hvor er du fra?",
      "Du virker chill 😎",
    ];

    replies.shuffle();
    return replies.first;
  }

  Future<String> sendToAI(String prompt) async {
    final response = await http.post(
      Uri.parse('http://10.0.2.2:8000/ai'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"prompt": prompt}),
    );

    final data = jsonDecode(response.body);
    return data["result"];
  }

  Future<String> getRealAIResponse(String userMessage) async {
    return sendToAI(userMessage);
  }

  void autoReply(String userMessage) async {
    final aiFuture = getRealAIResponse(userMessage);

    final fakeTypingDelay = Duration(
      milliseconds: 6000 + Random().nextInt(4000),
    );
    await Future.delayed(fakeTypingDelay);

    final reply = await aiFuture;
    if (!mounted) return;

    setState(() {
      messages.removeWhere((m) => m["isTyping"] == true);

      messages.add({
        "from": "alex",
        "text": reply,
        "isMe": false,
      });
    });

    if (scrollController.hasClients) {
      scrollController.animateTo(
        0,
        duration: Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.name),
        backgroundColor: Colors.pink,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              controller: scrollController,
              reverse: true, // 👈 VIKTIG
              children: messages.reversed.map((msg) {
                return Align(
                  alignment:
                      msg["isMe"] ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: EdgeInsets.symmetric(vertical: 5, horizontal: 10),
                    padding: EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: msg["isMe"] ? Colors.pink[200] : Colors.grey[300],
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(msg["text"]),
                  ),
                );
              }).toList(),
            ),
          ),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: controller,
                  textInputAction: TextInputAction.send,
                  decoration: InputDecoration(
                    hintText: "Skriv melding...",
                  ),
                  onSubmitted: (value) {
                    sendMessage();
                  },
                ),
              ),
              IconButton(
                icon: Icon(Icons.send),
                onPressed: sendMessage,
              )
            ],
          )
        ],
      ),
    );
  }
}
