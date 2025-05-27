<?php
if (!isset($_GET['user_id']) || empty($_GET['user_id'])) {
    header("Location: index.php");
    exit();
}
$user_id = $_GET['user_id'];
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Galleria Echo - Menu</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(120deg, #f6d365, #fda085);
            color: #333;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        header {
            width: 100%;
            text-align: center;
            background: #fda085;
            color: white;
            padding: 20px 0;
            position: relative;
        }

        .top-right {
            position: absolute;
            top: 20px;
            right: 20px;
        }

        .top-right a {
            color: white;
            text-decoration: none;
            font-weight: bold;
        }

        .subtitle {
            font-style: italic;
            font-size: 18px;
            margin-top: -10px;
            color: white;
        }

        .container {
            background: white;
            margin-top: 30px;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            width: 90%;
            max-width: 600px;
            text-align: center;
        }

        h2 {
            color: #fda085;
        }

        a.button {
            display: inline-block;
            margin: 15px;
            padding: 10px 20px;
            background: #fda085;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }

        .footer-logout {
            margin-top: 40px;
            text-align: center;
        }

        .footer-logout a {
            color: #fda085;
            text-decoration: none;
            font-weight: bold;
        }
    </style>
</head>
<body>

<header>
    <div class="top-right">
        <a href="index.php">Logout</a>
    </div>
    <h1>Welcome to Galleria Echo</h1>
    <p class="subtitle">"What You See... Might Not Stay."</p>
</header>

<div class="container">
    <h2>About Us</h2>
    <p>Discover timeless pieces and fleeting beauty. At Galleria Echo, art is more than aesthetics — it's an opportunity. Shop, explore and make yours what talks to your heart.</p>

    <h2>What would you like to do?</h2>
    <a href="create_order.php?user_id=<?= urlencode($user_id) ?>" class="button">Create New Order</a>
    <a href="manage_orders.php?user_id=<?= urlencode($user_id) ?>" class="button">Manage Orders</a>
</div>

<div class="footer-logout">
    <p><a href="index.php">Logout</a></p>
</div>

</body>
</html>
