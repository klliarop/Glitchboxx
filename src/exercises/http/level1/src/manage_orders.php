<?php
$host = getenv('DB_HOST') ?: '172.28.1.11';  // Get DB host from environment or use default
$user = getenv('DB_USER') ?: 'ctfuser';      // Get DB user from environment or use default
$pass = getenv('DB_PASS') ?: 'ctfpass';      // Get DB password from environment or use default
$db   = getenv('MYSQL_DATABASE') ?: 'ctf';   // Get DB name from environment or use default

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if (!isset($_GET['user_id']) || empty($_GET['user_id'])) {
    header("Location: index.php");
    exit();
}
$user_id = $_GET['user_id'];
$message = '';

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['update_order'])) {
    $order_id = $_POST['order_id'];
    $delivery_address = $conn->real_escape_string($_POST['delivery_address']);
    $status = $conn->real_escape_string($_POST['status']);

    // Use safe update by internal id
    $sql = "UPDATE orders SET delivery_address='$delivery_address', status='$status' WHERE id='$order_id' AND user_id='$user_id'";
    if ($conn->query($sql)) {
        $message = "<h2 style='color: green;'>Your flag is: <strong>f364ab19372c428cfd46370</strong></h2>";
    } else {
        $message = "<p style='color:red;'>Error updating order: " . $conn->error . "</p>";
    }
}

$search_result = null;
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['search'])) {
    $input_order_id = $conn->real_escape_string($_POST['order_id']);
    
    // Allow search by numeric `id` or custom `custom_order_id`
    $sql = "SELECT * FROM orders WHERE custom_order_id='$input_order_id' AND user_id='$user_id'";

    $search_result = $conn->query($sql);
}
?>


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Manage Orders — Galleria Echo</title>
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
            margin-bottom: 30px;
        }

        input[type="text"], textarea, select {
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
            color: green;
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
    </style>
</head>
<body>

<div class="top-link">
    <a href="menu.php?user_id=<?= urlencode($user_id) ?>" class="button"> Back to Menu</a>

</div>

<div class="header">
    <h1>Manage Orders</h1>
    <p class="subtitle">"What You See... Might Not Stay."</p>
    <p class="about">Discover timeless pieces and fleeting beauty. At Galleria Echo, art is more than aesthetics — it's an opportunity. Shop, explore and make yours what talks to your heart.</p>
</div>

<?php if (!empty($message)) echo "<div class='message'>$message</div>"; ?>

<form method="POST">
    <h3 style="margin-top: 0;">Find your order now</h3>
    <label>Order ID:</label>
    <input type="text" name="order_id" required>
    <button type="submit" name="search">Search</button>
</form>

<?php if ($search_result && $search_result->num_rows > 0): ?>
    <?php while($order = $search_result->fetch_assoc()): ?>
        <form method="POST">
            <input type="hidden" name="order_id" value="<?= $order['id'] ?>">
            <label><strong>Order ID:</strong> <?= htmlspecialchars($order['custom_order_id'] ?? $order['id']) ?></label><br><br>
            <label><strong>Product:</strong> <?= htmlspecialchars($order['product_name']) ?></label><br><br>
            <label><strong>Quantity:</strong> <?= $order['quantity'] ?></label><br><br>
            <label><strong>Delivery Address:</strong></label>
            <textarea name="delivery_address" rows="3"><?= htmlspecialchars($order['delivery_address']) ?></textarea>
            <label><strong>Status:</strong></label>
            <select name="status">
                <option value="pending" <?= $order['status'] == 'pending' ? 'selected' : '' ?>>Pending</option>
                <option value="shipped" <?= $order['status'] == 'shipped' ? 'selected' : '' ?>>Shipped</option>
                <option value="delivered" <?= $order['status'] == 'delivered' ? 'selected' : '' ?>>Delivered</option>
            </select>
            <button type="submit" name="update_order">Update Order</button>
        </form>
    <?php endwhile; ?>
<?php elseif ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['search'])): ?>
    <p style="color: white;">No orders found with that ID for your account.</p>
<?php endif; ?>

</body>
</html>
