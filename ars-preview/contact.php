<?php
/**
 * ARS Advocats i Assessors - Contact Form Backend Handler
 * Handles secure submission and email notification to info@arsadvocats.com
 */

header('Content-Type: application/json; charset=utf-8');

// Allow only POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method Not Allowed']);
    exit;
}

// 1. Anti-spam honeypot check (field hidden via CSS/JS)
if (!empty($_POST['website'])) {
    // Silent success for bots
    echo json_encode(['success' => true]);
    exit;
}

// 2. Extract and sanitize inputs
$name    = isset($_POST['name']) ? trim(strip_tags($_POST['name'])) : '';
$email   = isset($_POST['email']) ? trim(filter_var($_POST['email'], FILTER_SANITIZE_EMAIL)) : '';
$phone   = isset($_POST['phone']) ? trim(strip_tags($_POST['phone'])) : '';
$area    = isset($_POST['area']) ? trim(strip_tags($_POST['area'])) : '';
$message = isset($_POST['message']) ? trim(strip_tags($_POST['message'])) : '';
$consent = isset($_POST['consent']) && ($_POST['consent'] === '1' || $_POST['consent'] === 'on' || $_POST['consent'] === 'true');
$lang    = isset($_POST['lang']) && in_array($_POST['lang'], ['ca', 'es', 'en']) ? $_POST['lang'] : 'ca';
$fromChat = isset($_POST['from_chat']) && $_POST['from_chat'] === '1';

// 3. Validation
$errors = [];
if (empty($name)) {
    $errors[] = 'name_required';
}
if (empty($email) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    $errors[] = 'email_invalid';
}
if (empty($message)) {
    $errors[] = 'message_required';
}
if (!$consent) {
    $errors[] = 'consent_required';
}

if (!empty($errors)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'errors' => $errors]);
    exit;
}

// 4. Map area value to human-readable label
$areas = [
    'familia'             => 'Dret de família i matrimonial',
    'herencies'           => 'Successions, testaments i herències',
    'immobiliari'         => 'Immobiliari, arrendaments i desnonaments',
    'contractes'          => 'Obligacions i contractes',
    'quantitat'           => 'Reclamacions de quantitat',
    'comunitats'          => 'Comunitats de propietaris',
    'bancari'             => 'Dret bancari i clàusules abusives',
    'penal'               => 'Dret penal i litigació',
    'violencia'           => 'Violència masclista i de gènere',
    'compliance'          => 'Dret econòmic i compliance',
    'accidents'           => 'Accidents de trànsit i indemnitzacions',
    'laboral'             => 'Dret laboral i Seguretat Social',
    'incapacitats'        => 'Incapacitats laborals i invalidesa',
    'mercantil'           => 'Dret mercantil i societari',
    'segona-oportunitat'  => 'Dret concursal i segona oportunitat',
    'altres'              => 'Altres assumptes jurídics'
];
$areaLabel = isset($areas[$area]) ? $areas[$area] : ($area ? $area : 'No especificada');

// 5. Construct Email
$to = 'info@arsadvocats.com';
$subject = "Nova Consulta Web - ARS Advocats (" . ($name) . ")";

// Plain text email body
$body = "S'ha rebut una nova consulta des del formulari web d'ARS Advocats:\n\n";
$body .= "--------------------------------------------------------\n";
$body .= "Nom complet:       " . $name . "\n";
$body .= "Correu electrònic: " . $email . "\n";
$body .= "Telèfon:           " . (!empty($phone) ? $phone : "No indicat") . "\n";
$body .= "Àrea de consulta:  " . $areaLabel . "\n";
$body .= "Idioma web:        " . strtoupper($lang) . "\n";
$body .= "Data i hora:       " . date('d/m/Y H:i:s') . "\n";
$body .= "--------------------------------------------------------\n\n";
$body .= "Missatge del client:\n";
$body .= $message . "\n\n";
$body .= "--------------------------------------------------------\n";
$body .= "Consentiment RGPD acceptat expressament per l'usuari.\n";
$body .= "IP origen: " . (isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : 'desconeguda') . "\n";

// Headers
$headers = [];
$headers[] = 'From: ARS Advocats Web <info@arsadvocats.com>';
$headers[] = 'Reply-To: ' . $name . ' <' . $email . '>';
$headers[] = 'X-Mailer: PHP/' . phpversion();
$headers[] = 'Content-Type: text/plain; charset=UTF-8';

$sent = @mail($to, $subject, $body, implode("\r\n", $headers));

if ($sent) {
    // Server-side RGPD-compliant anonymous form counter (immune to adblockers)
    try {
        $statsDir  = __DIR__ . '/stats-data';
        $statsFile = $statsDir . '/metrics.json';
        if (!is_dir($statsDir)) {
            @mkdir($statsDir, 0750, true);
        }
        $fp = @fopen($statsFile, 'c+');
        if ($fp && flock($fp, LOCK_EX)) {
            rewind($fp);
            $content = stream_get_contents($fp);
            $data = json_decode($content ?: '', true);
            if (!is_array($data)) {
                $data = ['totals' => [], 'months' => [], 'days' => []];
            }
            $data['totals'] = isset($data['totals']) && is_array($data['totals']) ? $data['totals'] : [];
            $data['months'] = isset($data['months']) && is_array($data['months']) ? $data['months'] : [];
            $data['days']   = isset($data['days'])   && is_array($data['days'])   ? $data['days']   : [];

            $ev       = $fromChat ? 'web_form_from_chat' : 'web_form_direct';
            $monthKey = date('Y-m');
            $dayKey   = date('Y-m-d');

            if (!isset($data['months'][$monthKey]) || !is_array($data['months'][$monthKey])) {
                $data['months'][$monthKey] = [];
            }
            if (!isset($data['days'][$dayKey]) || !is_array($data['days'][$dayKey])) {
                $data['days'][$dayKey] = [];
            }

            $data['totals'][$ev]            = (int)($data['totals'][$ev] ?? 0) + 1;
            $data['months'][$monthKey][$ev] = (int)($data['months'][$monthKey][$ev] ?? 0) + 1;
            $data['days'][$dayKey][$ev]     = (int)($data['days'][$dayKey][$ev] ?? 0) + 1;

            if (count($data['days']) > 60) {
                ksort($data['days']);
                $data['days'] = array_slice($data['days'], -60, null, true);
            }

            $data['updated_at'] = date('c');

            ftruncate($fp, 0);
            rewind($fp);
            fwrite($fp, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
            fflush($fp);
            flock($fp, LOCK_UN);
            fclose($fp);
        }
    } catch (Throwable $e) {
        // Never affect form success response
    }

    echo json_encode(['success' => true]);
} else {
    // If local mail fails, return error
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'mail_error']);
}
