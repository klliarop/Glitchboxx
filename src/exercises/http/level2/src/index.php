<?php
$host = getenv('DB_HOST') ?: '172.29.0.11';
$user = getenv('DB_USER') ?: 'ctfuser2';
$pass = getenv('DB_PASS') ?: 'ctfpass2';
$db   = getenv('MYSQL_DATABASE') ?: 'ctf2';

// Connect to database
$conn = new mysqli($host, $user, $pass, $db);

if ($conn->connect_error) {
    http_response_code(500);
    die("Connection failed: " . $conn->connect_error);
}

// Process login
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $conn->real_escape_string($_POST['username']);
    $password = $conn->real_escape_string($_POST['password']);
    
    $sql = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        session_start();
        $row = $result->fetch_assoc();
        $_SESSION['loggedin'] = true;
        $_SESSION['username'] = $row['username'];
        header("Location: bank_account.php");
        exit();
    } else {
        http_response_code(401);
        echo "<div class='error'>Invalid credentials</div>";
    }
    exit();
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Private Network Access</title>
    <style>
        body {
            background-color: #0d1b2a;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
        }

        .container {
            margin-top: 8%;
        }

        h1 {
            color: #61dafb;
            font-size: 36px;
        }

        p {
            max-width: 600px;
            margin: 20px auto;
            font-size: 18px;
            line-height: 1.6;
            color: #c0c9d4;
        }

        form {
            margin-top: 40px;
            display: inline-block;
            background-color: #1b263b;
            padding: 30px 40px;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(0,0,0,0.4);
        }

        input[type="text"],
        input[type="password"] {
            width: 250px;
            padding: 10px;
            margin: 10px 0;
            border: none;
            border-radius: 5px;
            background-color: #415a77;
            color: white;
            font-size: 16px;
        }

        button {
            margin-top: 15px;
            padding: 10px 30px;
            background-color: #61dafb;
            color: #0d1b2a;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            background-color: #48bfe3;
        }

        .error {
            color: #ff6b6b;
            font-weight: bold;
            margin-top: 15px;
        }
    </style>
</head>
<body>


<body>
    <div class="container">
        <h1>WARNING: Restricted Network</h1>
        <p>
            This system is part of a secure and private network.<br>
            Access is strictly limited to authorized personnel only.
        </p>
        <p class="legal">
            Unauthorized access attempts are strictly prohibited.<br>
            All activity is monitored and logged and violators will be prosecuted.
        </p>
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required><br>
            <input type="password" name="password" placeholder="Password" required><br>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
