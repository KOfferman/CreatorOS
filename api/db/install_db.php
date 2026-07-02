<?php
/**
 * One-time Hostinger database installer (runs on the server via localhost MySQL).
 * 1. Upload this file + docs/schema.sql + docs/seed_data.sql to your site
 * 2. Visit: https://your-domain.com/install_db.php?secret=creatoros-install-2026
 * 3. Delete this file after success
 */
declare(strict_types=1);

$secret = getenv('INSTALL_DB_SECRET') ?: 'creatoros-install-2026';
if (($_GET['secret'] ?? '') !== $secret) {
    http_response_code(403);
    exit('Forbidden');
}

$configPath = __DIR__ . '/install_db.config.php';
if (!is_readable($configPath)) {
    http_response_code(500);
    exit('Missing install_db.config.php — copy install_db.config.example.php and fill in credentials.');
}

$config = require $configPath;
$host = $config['host'] ?? 'localhost';
$db   = $config['database'] ?? '';
$user = $config['username'] ?? '';
$pass = $config['password'] ?? '';

$mysqli = @new mysqli($host, $user, $pass, $db);
if ($mysqli->connect_error) {
    http_response_code(500);
    exit('Connect failed: ' . $mysqli->connect_error);
}

$mysqli->set_charset('utf8mb4');

$files = [
    __DIR__ . '/docs/schema.sql',
    __DIR__ . '/docs/seed_data.sql',
];

header('Content-Type: text/plain; charset=utf-8');
echo "CreatorOS DB installer\n\n";

foreach ($files as $file) {
    if (!is_readable($file)) {
        echo "Missing: $file\n";
        continue;
    }
    echo 'Running ' . basename($file) . "...\n";
    $sql = file_get_contents($file);
    if ($mysqli->multi_query($sql)) {
        do {
            if ($result = $mysqli->store_result()) {
                $result->free();
            }
        } while ($mysqli->more_results() && $mysqli->next_result());
    }
    echo $mysqli->error ? "  Error: {$mysqli->error}\n" : "  OK\n";
}

$res = $mysqli->query('SHOW TABLES');
echo "\nTables:\n";
while ($row = $res->fetch_row()) {
    echo " - {$row[0]}\n";
}
$mysqli->close();
