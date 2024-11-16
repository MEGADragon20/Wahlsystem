<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $passport_ID = $_POST['passport_ID']; 

    echo "passport ID: $passport_ID";
    echo "Verification code: $verif_code";
}
?>