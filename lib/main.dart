import 'dart:convert';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

String get baseUrl {
  if (kIsWeb) return 'http://127.0.0.1:8000';
  if (defaultTargetPlatform == TargetPlatform.android) {
    return 'http://10.0.2.2:8000';
  }
  return 'http://127.0.0.1:8000';
}

Future<String> sendToAI(String prompt) async {
  const personalities = [
    "Svar flørtete og leken, som en match med selvtillit.",
    "Svar morsomt og litt ertete, men varmt.",
    "Svar med litt attitude, sjarm og glimt i øyet.",
    "Svar rolig, trygg og ekte, som en person som er interessert.",
  ];

  try {
    final style = personalities[Random().nextInt(personalities.length)];

    final response = await http.post(
      Uri.parse('$baseUrl/ai'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "prompt": "Brukerens melding: $prompt\n\n$style\nHold svaret kort, naturlig og på norsk. Hvis brukeren ber om en bio, skriv en kort datingbio.",
      }),
    );

    print("STATUS: ${response.statusCode}");
    print("BODY: ${response.body}");

    final data = jsonDecode(utf8.decode(response.bodyBytes));
    return data["result"] ?? "Ingen svar";
  } catch (e) {
    print("ERROR: $e");
    return "FEIL: $e";
  }
}

List<Map<String, dynamic>> users = [
  {
    "name": "Alex",
    "age": 24,
    "image": "https://i.pravatar.cc/400?img=1",
    "bio": "Liker konserter, sene byturer og folk med glimt i øyet.",
    "city": "Oslo",
    "vibe": "Spontan ✨",
  },
  {
    "name": "Sam",
    "age": 27,
    "image": "https://i.pravatar.cc/400?img=2",
    "bio": "Kaffe, humor og roadtrips er min kjærlighetsspråk.",
    "city": "Bergen",
    "vibe": "Morsom 😄",
  },
  {
    "name": "Lina",
    "age": 22,
    "image": "https://i.pravatar.cc/400?img=3",
    "bio": "Myk energi, skarp humor og alltid klar for nye eventyr.",
    "city": "Trondheim",
    "vibe": "Flørtete 💕",
  },
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
  double x = 0;
  double y = 0;
  int currentIndex = 0;
  final List<Map<String, dynamic>> likedUsers = [];

  void handleLike() {
    if (currentIndex >= users.length) return;

    final matchedUser = users[currentIndex];

    setState(() {
      likedUsers.add(matchedUser);
      currentIndex++;
      x = 0;
      y = 0;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text("It’s a match med ${matchedUser['name']} 💘"),
        backgroundColor: Colors.pink,
      ),
    );

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatPage(name: matchedUser['name']),
      ),
    );
  }

  void handleNope() {
    if (currentIndex >= users.length) return;

    setState(() {
      currentIndex++;
      x = 0;
      y = 0;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFFFFF5FA),
      appBar: AppBar(
        title: Text("Regnbuematch 🌈"),
        centerTitle: true,
        backgroundColor: Colors.pink,
      ),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Swipe for å finne en vibe ✨",
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 6),
            Text(
              "Lik for match og åpne chat med én gang.",
              style: TextStyle(color: Colors.black54),
            ),
            SizedBox(height: 16),
            Expanded(
              child: currentIndex >= users.length
                  ? buildMatchesView()
                  : Center(
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          if (currentIndex + 1 < users.length)
                            Opacity(
                              opacity: 0.55,
                              child: buildCardAt(currentIndex + 1, scale: 0.95),
                            ),
                          buildDraggableCard(),
                        ],
                      ),
                    ),
            ),
            if (currentIndex < users.length) ...[
              SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  buildActionButton(
                    icon: Icons.close,
                    color: Colors.grey.shade700,
                    onTap: handleNope,
                  ),
                  buildActionButton(
                    icon: Icons.favorite,
                    color: Colors.pink,
                    onTap: handleLike,
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget buildMatchesView() {
    if (likedUsers.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text("Ingen matcher ennå 💔", style: TextStyle(fontSize: 22)),
            SizedBox(height: 12),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  currentIndex = 0;
                  x = 0;
                  y = 0;
                });
              },
              child: Text("Prøv igjen"),
            ),
          ],
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          "Dine matcher 💘",
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        SizedBox(height: 12),
        Expanded(
          child: ListView.builder(
            itemCount: likedUsers.length,
            itemBuilder: (context, index) {
              final user = likedUsers[index];
              return Card(
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundImage: NetworkImage(user['image']),
                  ),
                  title: Text(user['name']),
                  subtitle: Text(user['bio']),
                  trailing: Icon(Icons.chat_bubble, color: Colors.pink),
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => ChatPage(name: user['name']),
                      ),
                    );
                  },
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget buildDraggableCard() {
    final user = users[currentIndex];

    return GestureDetector(
      onPanUpdate: (details) {
        setState(() {
          x += details.delta.dx;
          y += details.delta.dy * 0.15;
        });
      },
      onPanEnd: (_) {
        if (x > 110) {
          handleLike();
        } else if (x < -110) {
          handleNope();
        } else {
          setState(() {
            x = 0;
            y = 0;
          });
        }
      },
      child: AnimatedContainer(
        duration: Duration(milliseconds: 220),
        curve: Curves.easeOut,
        transform: Matrix4.identity()
          ..translate(x, y)
          ..rotateZ(x / 500),
        child: Stack(
          children: [
            buildCardContent(user),
            if (x > 20)
              Positioned(
                top: 20,
                left: 20,
                child: buildStamp("LIKE", Colors.green),
              ),
            if (x < -20)
              Positioned(
                top: 20,
                right: 20,
                child: buildStamp("NOPE", Colors.red),
              ),
          ],
        ),
      ),
    );
  }

  Widget buildCardAt(int index, {double scale = 1}) {
    return Transform.scale(
      scale: scale,
      child: buildCardContent(users[index]),
    );
  }

  Widget buildCardContent(Map<String, dynamic> user) {
    return Container(
      width: 330,
      height: 510,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(26),
        boxShadow: [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 18,
            offset: Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.vertical(top: Radius.circular(26)),
            child: Image.network(
              user['image'],
              height: 290,
              width: double.infinity,
              fit: BoxFit.cover,
            ),
          ),
          Padding(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        "${user['name']}, ${user['age']}",
                        style: TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    Icon(Icons.verified, color: Colors.pink),
                  ],
                ),
                SizedBox(height: 6),
                Text(
                  "${user['city']} • ${user['vibe']}",
                  style: TextStyle(color: Colors.black54, fontSize: 15),
                ),
                SizedBox(height: 12),
                Text(
                  user['bio'],
                  style: TextStyle(fontSize: 16, height: 1.35),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget buildActionButton({
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.white,
      shape: CircleBorder(),
      elevation: 4,
      child: InkWell(
        customBorder: CircleBorder(),
        onTap: onTap,
        child: Padding(
          padding: EdgeInsets.all(18),
          child: Icon(icon, color: color, size: 28),
        ),
      ),
    );
  }

  Widget buildStamp(String label, Color color) {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        border: Border.all(color: color, width: 3),
        borderRadius: BorderRadius.circular(10),
        color: Colors.white.withOpacity(0.92),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.bold,
          fontSize: 22,
        ),
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

  @override
  void initState() {
    super.initState();
    messages.add({
      "text": "Hei 😏 Jeg er ${widget.name}. Skal vi se om vi har vibe?",
      "isMe": false,
    });
  }

  void sendMessage() async {
    if (controller.text.trim().isEmpty) return;

    String userText = controller.text.trim();

    setState(() {
      messages.add({
        "text": userText,
        "isMe": true,
      });
      messages.add({
        "text": "${widget.name} skriver...",
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

  Future<String> getRealAIResponse(String userMessage) async {
    return await sendToAI(
      "Du er ${widget.name} i en datingchat. Svar naturlig og kort på: $userMessage",
    );
  }

  void autoReply(String userMessage) async {
    final fakeTypingDelay = Duration(
      milliseconds: 4500 + Random().nextInt(3500),
    );
    await Future.delayed(fakeTypingDelay);

    String reply;
    try {
      reply = await getRealAIResponse(userMessage);
    } catch (_) {
      reply = "Oops 😅 Jeg datt litt ut der. Send igjen?";
    }

    if (!mounted) return;

    setState(() {
      messages.removeWhere((m) => m["isTyping"] == true);

      messages.add({
        "from": widget.name.toLowerCase(),
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
              reverse: true,
              padding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              children: messages.reversed.map((msg) {
                final isMe = msg["isMe"] == true;

                return Align(
                  alignment:
                      isMe ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: EdgeInsets.symmetric(vertical: 4),
                    padding: EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    constraints: BoxConstraints(maxWidth: 280),
                    decoration: BoxDecoration(
                      gradient: isMe
                          ? LinearGradient(
                              colors: [
                                Colors.pink.shade400,
                                Colors.deepPurple.shade300,
                              ],
                            )
                          : null,
                      color: isMe ? null : Colors.grey.shade200,
                      borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(18),
                        topRight: Radius.circular(18),
                        bottomLeft: Radius.circular(isMe ? 18 : 6),
                        bottomRight: Radius.circular(isMe ? 6 : 18),
                      ),
                    ),
                    child: Text(
                      msg["text"],
                      style: TextStyle(
                        color: isMe ? Colors.white : Colors.black87,
                        fontSize: 15,
                        height: 1.35,
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          SafeArea(
            top: false,
            child: Padding(
              padding: EdgeInsets.fromLTRB(12, 4, 12, 12),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: controller,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => sendMessage(),
                      decoration: InputDecoration(
                        hintText: "Skriv melding...",
                        filled: true,
                        fillColor: Colors.white,
                        contentPadding: EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 12,
                        ),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                      ),
                    ),
                  ),
                  SizedBox(width: 8),
                  Material(
                    color: Colors.pink,
                    borderRadius: BorderRadius.circular(24),
                    child: InkWell(
                      borderRadius: BorderRadius.circular(24),
                      onTap: sendMessage,
                      child: Padding(
                        padding: EdgeInsets.all(12),
                        child: Icon(Icons.send, color: Colors.white),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
