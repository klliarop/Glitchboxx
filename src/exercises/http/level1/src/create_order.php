<?php
$host = getenv('DB_HOST') ?: '172.28.1.11';  // Get DB host from environment or use default
$user = getenv('DB_USER') ?: 'ctfuser';      // Get DB user from environment or use default
$pass = getenv('DB_PASS') ?: 'ctfpass';      // Get DB password from environment or use default
$db   = getenv('MYSQL_DATABASE') ?: 'ctf';   // Get DB name from environment or use default

// Connect to MySQL database
$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Check that user_id exists and is not empty in GET parameters
if (!isset($_GET['user_id']) || empty($_GET['user_id'])) {
    header("Location: index.php");
    exit();
}
$user_id = $_GET['user_id'];

$message = '';

// If form is submitted via POST, process the order creation
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $product_name = $_POST['product_name'];
    $quantity = $_POST['quantity'];
    $delivery_address = $_POST['delivery_address'];
    
    // Insert the new order into the database
    $sql = "INSERT INTO orders (user_id, product_name, quantity, delivery_address) 
            VALUES ('$user_id', '$product_name', '$quantity', '$delivery_address')";
    
    if ($conn->query($sql)) {
        $message = "<p style='color: green; font-weight: bold;'>Order created successfully!</p>";
    } else {
        $message = "<p style='color: red;'>Error: " . $conn->error . "</p>";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Create Order — Galleria Echo</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(120deg, #f6d365, #fda085);
            color: #333;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 60px 20px 40px;
        }

        .top-link {
            position: absolute;
            top: 20px;
            left: 20px;
        }

        .top-link a {
            background: white;
            padding: 10px 15px;
            border-radius: 5px;
            color: #fda085;
            font-weight: bold;
            text-decoration: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }

        .top-link a:hover {
            background: #fda085;
            color: white;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        h1 {
            background: #fda085;
            color: white;
            padding: 15px 30px;
            border-radius: 10px;
            margin-bottom: 10px;
        }

        .subtitle {
            color: white;
            font-size: 18px;
            margin-bottom: 10px;
        }

        .about {
            color: white;
            max-width: 500px;
            font-size: 16px;
            margin-bottom: 40px;
        }

        form {
            background: #fff;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 600px;
        }

        input[type="text"],
        input[type="number"],
        textarea {
            width: 100%;
            padding: 10px;
            margin-top: 8px;
            margin-bottom: 15px;
            border-radius: 5px;
            border: 1px solid #ccc;
            font-size: 15px;
        }

        button {
            padding: 10px 20px;
            background-color: #fda085;
            border: none;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }

        .message {
            margin: 20px 0;
            font-size: 18px;
        }
    </style>
</head>
<body>
<div class="top-link">
    <a href="menu.php?user_id=<?= urlencode($user_id) ?>" class="button">Back to Menu</a>
</div>

<div class="header">
    <h1>Create New Order</h1>
    <p class="subtitle">"What You See... Might Not Stay."</p>
    <p class="about">Each order is a brushstroke in your masterpiece. At Galleria Echo, beauty is fleeting — but your timing doesn't have to be.</p>
</div>

<?php if (!empty($message)) echo "<div class='message'>$message</div>"; ?>

<form method="POST">
    <label>Product Name:</label>
    <input type="text" name="product_name" required>

    <label>Quantity:</label>
    <input type="number" name="quantity" min="1" required>

    <label>Delivery Address:</label>
    <textarea name="delivery_address" rows="3" required></textarea>

    <button type="submit">Create Order</button>
</form>

</body>
</html>
