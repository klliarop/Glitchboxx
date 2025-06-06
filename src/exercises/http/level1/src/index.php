<?php
$host = getenv('DB_HOST') ?: '172.28.1.11';  // Get DB host from environment or use default
$user = getenv('DB_USER') ?: 'ctfuser';      // Get DB user from environment or use default
$pass = getenv('DB_PASS') ?: 'ctfpass';      // Get DB password from environment or use default
$db   = getenv('MYSQL_DATABASE') ?: 'ctf';   // Get DB name from environment or use default

$conn = new mysqli($host, $user, $pass, $db);  // Connect to MySQL database

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);  // Stop if connection fails
}

$login_message = '';
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // Sanitize inputs (not perfect, but improves security a bit)
    $username = $conn->real_escape_string($username);
    $password = $conn->real_escape_string($password);

    $sql = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        $user = $result->fetch_assoc();
        $user_id = $user['id'];

        // Redirect to menu with user_id if login is successful
        header("Location: menu.php?user_id=" . urlencode($user_id));
        exit();
    } else {
        $login_message = "Invalid credentials.";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Galleria Echo</title>
    <style>
        .title {
            background: #fda085;
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 36px;
            margin-bottom: 10px;
        }

        .subtitle {
            color: white;
            font-size: 18px;
            margin-bottom: 40px; /* adds space before login box */
        }

        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(120deg, #f6d365, #fda085);
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        h1 {
            color: #fff;
            margin-bottom: 20px;
        }

        form {
            background: #ffffff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            text-align: center;
            width: 300px; /* Ensures a consistent form size */
            display: flex;
            flex-direction: column;
            gap: 15px; /* Clean spacing between fields */
        }

        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            border: 1px solid #ccc;
            font-size: 16px;
            box-sizing: border-box;
        }

        button {
            padding: 10px 20px;
            background: #fda085;
            border: none;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }

        .message {
            margin-top: 10px;
            color: red;
        }
    </style>
</head>
<body>

<h1 class="title">Galleria Echo</h1>
<p class="subtitle">"Every Masterpiece Leaves a Trace"</p>

<form method="POST">
    <input type="text" name="username" placeholder="Username" required><br>
    <input type="password" name="password" placeholder="Password" required><br>
    <button type="submit">Login</button>
</form>


<?php if (!empty($login_message)) echo "<div class='message'>$login_message</div>"; ?>

</body>
</html>
