<?php
session_start();
if (!isset($_SESSION['loggedin'])) {
    header("Location: index.php");
    exit();
}

if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['make_payment'])) {
    die('
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Payment Completed</title>
        <style>
            body {
                background-color: #e6f2ff;
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }

            // .flag-container {
            //     background-color: #ffffff;
            //     border-left: 6px solid #3399ff;
            //     padding: 30px 40px;
            //     border-radius: 10px;
            //     box-shadow: 0 0 15px rgba(0, 102, 204, 0.2);
            //     text-align: center;
            //     max-width: 500px;
            // }

            // .flag-container h1 {
            //     color: #004080;
            //     margin-bottom: 10px;
            // }

            .flag-container p {
                font-size: 18px;
                color: #003366;
                word-break: break-all;
            }
        </style>
    </head>
    <body>
        <div class="flag-container">
            <p><strong>  🎉 FLAG:</strong> 7a5f8d3e1c9b24680a42d59</p>
        </div>
    </body>
    </html>
    ');

   
   
   
   
    // die("FLAG: 7a5f8d3e1c9b24680a42d59"); // Stops execution and shows only flag
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Septemtica Bank</title>
    <style>
        body {
            background-color: #e6f2ff; /* light blue */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #003366;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }

        h1 {
            color: #004080;
            font-size: 36px;
            margin-bottom: 10px;
        }

        h2 {
            color: #0059b3;
            margin-bottom: 40px;
        }

        form {
            background-color: #ffffff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0, 102, 204, 0.2);
            text-align: center;
        }

        input[type="number"],
        input[type="text"] {
            width: 90%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #cccccc;
            border-radius: 5px;
            font-size: 16px;
        }

        button {
            background-color: #3399ff;
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        button:hover {
            background-color: #007acc;
        }
    </style>
</head>
<body>
    <h1>Septemtica Bank Emergency Page</h1>
    <h2>Your Deposit: €5,032.00</h2>
    <h2>⚠️ Warning! Access to this section is strictly limited. <br>
        <strong>You must obtain explicit permission from an authorized <br> supervisor or administrator before proceeding.</strong>
    </h2>

    <form method="POST">
        <input type="number" name="amount" placeholder="Amount" required><br>
        <input type="text" name="mobile" placeholder="Mobile" required><br>
        <button type="submit" name="make_payment">Complete Iris Payment</button>
    </form>
</body>
</html>
