<?php
/**
 * ARS Advocats i Assessors — Panell d'Estadístiques Anònimes (RGPD 100%)
 * - POST: Registra comptadors anònims (sense IPs, sense cookies, sense textos).
 * - GET (?k=SECRET): Mostra el panell corporatiu privat (noindex, nofollow).
 */

header('X-Robots-Tag: noindex, nofollow, noarchive', true);
date_default_timezone_set('Europe/Madrid');

define('ARS_STATS_KEY', 'ars2026-8f4c9a2e');
define('ARS_DATA_DIR', __DIR__ . '/stats-data');
define('ARS_DATA_FILE', ARS_DATA_DIR . '/metrics.json');

$ALLOWED_EVENTS = [
    'visit_google',
    'visit_ai',
    'ai_chatgpt',
    'ai_perplexity',
    'ai_gemini',
    'ai_claude',
    'ai_other',
    'visit_social',
    'visit_direct',
    'chat_open',
    'chat_session',
    'chat_message',
    'chat_to_wa',
    'chat_to_form',
    'web_wa',
    'web_tel',
    'web_mailto',
    'web_form_direct',
    'web_form_from_chat',
    'lang_ca',
    'lang_es',
    'lang_en',
    'area_familia',
    'area_herencies',
    'area_immobiliari',
    'area_contractes',
    'area_quantitat',
    'area_comunitats',
    'area_bancari',
    'area_penal',
    'area_violencia',
    'area_compliance',
    'area_accidents',
    'area_laboral',
    'area_incapacitats',
    'area_mercantil',
    'area_segona_oportunitat',
    'area_altres',
];

$AREA_LABELS = [
    'area_familia'            => 'Família i matrimonial',
    'area_laboral'            => 'Laboral i Seguretat Social',
    'area_herencies'          => 'Herències i successions',
    'area_immobiliari'        => 'Desnonaments i lloguers',
    'area_penal'              => 'Penal i litigació',
    'area_violencia'          => 'Violència de gènere',
    'area_accidents'          => 'Accidents de trànsit',
    'area_bancari'            => 'Bancari i clàusules',
    'area_comunitats'         => 'Comunitats de propietaris',
    'area_quantitat'          => 'Reclamacions de quantitat',
    'area_contractes'         => 'Obligacions i contractes',
    'area_incapacitats'       => 'Incapacitats laborals',
    'area_mercantil'          => 'Mercantil i societari',
    'area_segona_oportunitat' => 'Concursal i segona oportunitat',
    'area_compliance'         => 'Delictes econòmics i compliance',
    'area_altres'             => 'Altres assumptes',
];

function ars_load_data($file) {
    if (!file_exists($file)) {
        return ['totals' => [], 'months' => [], 'days' => []];
    }
    $raw = @file_get_contents($file);
    $data = json_decode($raw ?: '', true);
    if (!is_array($data)) {
        return ['totals' => [], 'months' => [], 'days' => []];
    }
    $data['totals'] = isset($data['totals']) && is_array($data['totals']) ? $data['totals'] : [];
    $data['months'] = isset($data['months']) && is_array($data['months']) ? $data['months'] : [];
    $data['days']   = isset($data['days'])   && is_array($data['days'])   ? $data['days']   : [];
    return $data;
}

// =========================================================================
// 1. POST: REGISTRE ANÒNIM D'ESDEVENIMENTS
// =========================================================================
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Validar origen (només arsadvocats.com o localhost)
    $origin  = $_SERVER['HTTP_ORIGIN']  ?? '';
    $referer = $_SERVER['HTTP_REFERER'] ?? '';
    $source  = $origin ?: $referer;
    $host    = $source ? (parse_url($source, PHP_URL_HOST) ?: '') : '';
    $validHost = in_array($host, ['www.arsadvocats.com', 'arsadvocats.com', 'localhost', '127.0.0.1'], true);

    if (!$validHost) {
        http_response_code(403);
        exit;
    }

    $rawBody = file_get_contents('php://input');
    $payload = json_decode($rawBody ?: '', true);

    // Optional admin date rebalance (protected by ARS_STATS_KEY)
    if (
        is_array($payload) &&
        isset($payload['admin_key']) &&
        is_string($payload['admin_key']) &&
        hash_equals(ARS_STATS_KEY, $payload['admin_key']) &&
        isset($payload['adjust']) &&
        is_array($payload['adjust'])
    ) {
        if (!is_dir(ARS_DATA_DIR)) {
            @mkdir(ARS_DATA_DIR, 0750, true);
        }
        $fp = @fopen(ARS_DATA_FILE, 'c+');
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

            foreach ($payload['adjust'] as $item) {
                if (!is_array($item)) continue;
                $day   = isset($item['day']) && is_string($item['day']) ? $item['day'] : '';
                $ev    = isset($item['event']) && is_string($item['event']) ? $item['event'] : '';
                $delta = isset($item['delta']) ? (int)$item['delta'] : 0;
                if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $day) || !in_array($ev, $ALLOWED_EVENTS, true) || $delta === 0) {
                    continue;
                }
                $ym = substr($day, 0, 7);
                if (!isset($data['months'][$ym]) || !is_array($data['months'][$ym])) {
                    $data['months'][$ym] = [];
                }
                if (!isset($data['days'][$day]) || !is_array($data['days'][$day])) {
                    $data['days'][$day] = [];
                }
                $data['totals'][$ev]       = max(0, (int)($data['totals'][$ev] ?? 0) + $delta);
                $data['months'][$ym][$ev]  = max(0, (int)($data['months'][$ym][$ev] ?? 0) + $delta);
                $data['days'][$day][$ev]   = max(0, (int)($data['days'][$day][$ev] ?? 0) + $delta);
            }

            $data['updated_at'] = date('c');
            ftruncate($fp, 0);
            rewind($fp);
            fwrite($fp, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
            fflush($fp);
            flock($fp, LOCK_UN);
            fclose($fp);
        }
        http_response_code(204);
        exit;
    }

    $events = [];

    if (is_array($payload)) {
        if (isset($payload['events']) && is_array($payload['events'])) {
            $events = $payload['events'];
        } elseif (isset($payload['event']) && is_string($payload['event'])) {
            $events = [$payload['event']];
        }
    } elseif (isset($_POST['event']) && is_string($_POST['event'])) {
        $events = [$_POST['event']];
    }

    // Filtrar només esdeveniments permesos (màxim 6 per petició)
    $validEvents = [];
    foreach (array_slice($events, 0, 6) as $ev) {
        if (is_string($ev) && in_array($ev, $ALLOWED_EVENTS, true)) {
            $validEvents[] = $ev;
        }
    }

    if (empty($validEvents)) {
        http_response_code(400);
        exit;
    }

    if (!is_dir(ARS_DATA_DIR)) {
        @mkdir(ARS_DATA_DIR, 0750, true);
    }

    $fp = @fopen(ARS_DATA_FILE, 'c+');
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

        $monthKey = date('Y-m');
        $dayKey   = date('Y-m-d');

        if (!isset($data['months'][$monthKey]) || !is_array($data['months'][$monthKey])) {
            $data['months'][$monthKey] = [];
        }
        if (!isset($data['days'][$dayKey]) || !is_array($data['days'][$dayKey])) {
            $data['days'][$dayKey] = [];
        }

        foreach ($validEvents as $ev) {
            $data['totals'][$ev]            = (int)($data['totals'][$ev] ?? 0) + 1;
            $data['months'][$monthKey][$ev] = (int)($data['months'][$monthKey][$ev] ?? 0) + 1;
            $data['days'][$dayKey][$ev]     = (int)($data['days'][$dayKey][$ev] ?? 0) + 1;
        }

        // Retenir només els últims 60 dies a 'days' per mantenir l'arxiu lleuger
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

    http_response_code(204);
    exit;
}

// =========================================================================
// 2. GET: PANELL CORPORATIU PRIVAT (PROTEGIT AMB CLAU)
// =========================================================================
$key = isset($_GET['k']) && is_string($_GET['k']) ? $_GET['k'] : '';
if (!hash_equals(ARS_STATS_KEY, $key)) {
    http_response_code(404);
    exit;
}

header('Content-Type: text/html; charset=UTF-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');

$data = ars_load_data(ARS_DATA_FILE);
$currentMonth = date('Y-m');
$availableMonths = array_keys($data['months']);
if (!in_array($currentMonth, $availableMonths, true)) {
    $availableMonths[] = $currentMonth;
}
rsort($availableMonths);

$selectedPeriod = isset($_GET['m']) && is_string($_GET['m']) ? $_GET['m'] : $currentMonth;
if ($selectedPeriod !== 'all' && !in_array($selectedPeriod, $availableMonths, true)) {
    $selectedPeriod = $currentMonth;
}

$m = ($selectedPeriod === 'all')
    ? $data['totals']
    : ($data['months'][$selectedPeriod] ?? []);

$val = function ($k) use ($m) {
    return (int)($m[$k] ?? 0);
};

// Mètriques agregades
$vGoogle = $val('visit_google');
$vAi     = $val('visit_ai');
$vSocial = $val('visit_social');
$vDirect = $val('visit_direct');
$vTotal  = $vGoogle + $vAi + $vSocial + $vDirect;

$aiChatgpt    = $val('ai_chatgpt');
$aiPerplexity = $val('ai_perplexity');
$aiGemini     = $val('ai_gemini');
$aiClaude     = $val('ai_claude');
$aiOther      = $val('ai_other');

$chatOpen     = $val('chat_open');
$chatSessions = $val('chat_session');
$chatMsg      = $val('chat_message');
$chatToWa     = $val('chat_to_wa');
$chatToForm   = $val('chat_to_form');

$webWa           = $val('web_wa');
$webTel          = $val('web_tel');
$webMailto       = $val('web_mailto');
$webFormDirect   = $val('web_form_direct');
$webFormFromChat = $val('web_form_from_chat');

$totalWa      = $webWa + $chatToWa;
$totalForm    = $webFormDirect + $webFormFromChat;
$totalDirectC = $totalWa + $webTel + $webMailto;
$totalLeads   = $totalWa + $totalForm + $webTel + $webMailto;

$langCa    = $val('lang_ca');
$langEs    = $val('lang_es');
$langEn    = $val('lang_en');
$langTotal = $langCa + $langEs + $langEn;

$areaCounts = [];
foreach ($AREA_LABELS as $aKey => $aLabel) {
    $c = $val($aKey);
    if ($c > 0) {
        $areaCounts[$aKey] = $c;
    }
}
arsort($areaCounts);
$areaTotal = array_sum($areaCounts);

$pct = function ($part, $whole) {
    if ($whole <= 0) return 0;
    return round(($part / $whole) * 100);
};

$chatActions = $chatToWa + $chatToForm;
$chatConvBase = $chatSessions > 0 ? $chatSessions : $chatOpen;
$chatConvBaseLabel = $chatSessions > 0 ? 'converses' : 'obertures';
$chatConvRate = $chatConvBase > 0 ? round(($chatActions / $chatConvBase) * 100, 1) : 0;

// Últims 14 dies per al gràfic diari
$last14 = [];
$maxDayVal = 1;
for ($i = 13; $i >= 0; $i--) {
    $d = date('Y-m-d', strtotime("-{$i} days"));
    $dm = $data['days'][$d] ?? [];
    $dVisits = (int)($dm['visit_google'] ?? 0) + (int)($dm['visit_ai'] ?? 0) + (int)($dm['visit_social'] ?? 0) + (int)($dm['visit_direct'] ?? 0);
    $dChat   = (int)($dm['chat_message'] ?? 0);
    $dLeads  = (int)($dm['chat_to_wa'] ?? 0) + (int)($dm['web_wa'] ?? 0) + (int)($dm['web_form_direct'] ?? 0) + (int)($dm['web_form_from_chat'] ?? 0);
    $maxDayVal = max($maxDayVal, $dVisits, $dChat, $dLeads);
    $last14[] = [
        'label'  => date('d/m', strtotime($d)),
        'visits' => $dVisits,
        'chat'   => $dChat,
        'leads'  => $dLeads,
    ];
}

$monthNames = [
    '01' => 'Gen', '02' => 'Feb', '03' => 'Mar', '04' => 'Abr',
    '05' => 'Mai', '06' => 'Jun', '07' => 'Jul', '08' => 'Ago',
    '09' => 'Set', '10' => 'Oct', '11' => 'Nov', '12' => 'Des',
];
$formatMonth = function ($ym) use ($monthNames) {
    $parts = explode('-', $ym);
    if (count($parts) !== 2) return $ym;
    return ($monthNames[$parts[1]] ?? $parts[1]) . ' ' . $parts[0];
};

$updatedLabel = !empty($data['updated_at'])
    ? date('d/m/Y · H:i', strtotime($data['updated_at']))
    : 'Sense activitat registrada encara';

// Agregació per mesos (12 mesos per cada any disponible) i per anys
$yearsSet = [date('Y') => true];
foreach (array_keys($data['months']) as $ymKey) {
    $yPart = substr($ymKey, 0, 4);
    if (preg_match('/^\d{4}$/', $yPart)) {
        $yearsSet[$yPart] = true;
    }
}
$availableYears = array_keys($yearsSet);
sort($availableYears);

$extractRow = function ($bucket) {
    $visits   = (int)($bucket['visit_google'] ?? 0) + (int)($bucket['visit_ai'] ?? 0) + (int)($bucket['visit_social'] ?? 0) + (int)($bucket['visit_direct'] ?? 0);
    $google   = (int)($bucket['visit_google'] ?? 0);
    $ai       = (int)($bucket['visit_ai'] ?? 0);
    $sessions = (int)($bucket['chat_session'] ?? 0);
    $chat     = (int)($bucket['chat_message'] ?? 0);
    $wa       = (int)($bucket['chat_to_wa'] ?? 0) + (int)($bucket['web_wa'] ?? 0);
    $tel      = (int)($bucket['web_tel'] ?? 0);
    $mailto   = (int)($bucket['web_mailto'] ?? 0);
    $form     = (int)($bucket['web_form_direct'] ?? 0) + (int)($bucket['web_form_from_chat'] ?? 0);
    return [
        'visits'   => $visits,
        'google'   => $google,
        'ai'       => $ai,
        'sessions' => $sessions,
        'chat'     => $chat,
        'wa'       => $wa,
        'tel'      => $tel,
        'mailto'   => $mailto,
        'form'     => $form,
        'leads'    => $wa + $form + $tel + $mailto,
    ];
};

$monthlyByYear   = [];
$quarterlyByYear = [];
$yearlySeries    = [];
foreach ($availableYears as $yr) {
    $monthlyByYear[$yr] = [];
    $quarters = [
        1 => ['label' => 'T1', 'fullLabel' => "T1 {$yr} (Gen–Mar)", 'visits' => 0, 'google' => 0, 'ai' => 0, 'sessions' => 0, 'chat' => 0, 'wa' => 0, 'tel' => 0, 'mailto' => 0, 'form' => 0, 'leads' => 0],
        2 => ['label' => 'T2', 'fullLabel' => "T2 {$yr} (Abr–Jun)", 'visits' => 0, 'google' => 0, 'ai' => 0, 'sessions' => 0, 'chat' => 0, 'wa' => 0, 'tel' => 0, 'mailto' => 0, 'form' => 0, 'leads' => 0],
        3 => ['label' => 'T3', 'fullLabel' => "T3 {$yr} (Jul–Set)", 'visits' => 0, 'google' => 0, 'ai' => 0, 'sessions' => 0, 'chat' => 0, 'wa' => 0, 'tel' => 0, 'mailto' => 0, 'form' => 0, 'leads' => 0],
        4 => ['label' => 'T4', 'fullLabel' => "T4 {$yr} (Oct–Des)", 'visits' => 0, 'google' => 0, 'ai' => 0, 'sessions' => 0, 'chat' => 0, 'wa' => 0, 'tel' => 0, 'mailto' => 0, 'form' => 0, 'leads' => 0],
    ];
    $yrTotals = ['label' => $yr, 'visits' => 0, 'google' => 0, 'ai' => 0, 'sessions' => 0, 'chat' => 0, 'wa' => 0, 'tel' => 0, 'mailto' => 0, 'form' => 0, 'leads' => 0];
    foreach ($monthNames as $mm => $mLabel) {
        $ymKey = "{$yr}-{$mm}";
        $row = $extractRow($data['months'][$ymKey] ?? []);
        $row['label'] = $mLabel;
        $row['fullLabel'] = "{$mLabel} {$yr}";
        $monthlyByYear[$yr][] = $row;
        $qIdx = (int)ceil(((int)$mm) / 3);
        foreach (['visits', 'google', 'ai', 'sessions', 'chat', 'wa', 'tel', 'mailto', 'form', 'leads'] as $f) {
            $quarters[$qIdx][$f] += $row[$f];
            $yrTotals[$f] += $row[$f];
        }
    }
    $quarterlyByYear[$yr] = array_values($quarters);
    $yrTotals['fullLabel'] = "Any {$yr}";
    $yearlySeries[] = $yrTotals;
}

// Sèries diàries (últims 7 i 30 dies)
$buildDailySeries = function ($numDays) use ($data, $extractRow) {
    $out = [];
    for ($i = $numDays - 1; $i >= 0; $i--) {
        $ts = strtotime("-{$i} days");
        $dKey = date('Y-m-d', $ts);
        $row = $extractRow($data['days'][$dKey] ?? []);
        $row['label'] = date('d/m', $ts);
        $row['fullLabel'] = date('d/m/Y', $ts);
        $out[] = $row;
    }
    return $out;
};

$chartPayload = [
    'currentYear'     => date('Y'),
    'years'           => array_reverse($availableYears),
    'days7'           => $buildDailySeries(7),
    'days30'          => $buildDailySeries(30),
    'monthlyByYear'   => $monthlyByYear,
    'quarterlyByYear' => $quarterlyByYear,
    'yearly'          => $yearlySeries,
];

$reqPath = parse_url($_SERVER['REQUEST_URI'] ?? '', PHP_URL_PATH) ?: '';
$isPrettyUrl = (strpos($reqPath, '/panell-ars') === 0);
$buildUrl = function ($period, $extra = '') use ($isPrettyUrl, $key) {
    $base = $isPrettyUrl
        ? '/panell-ars?m=' . urlencode($period)
        : '?k=' . urlencode($key) . '&m=' . urlencode($period);
    return $extra ? $base . '&' . $extra : $base;
};

// =========================================================================
// 2b. EXPORTACIÓ CSV DEL PERÍODE SELECCIONAT
// =========================================================================
if (isset($_GET['export']) && $_GET['export'] === 'csv') {
    $safePeriod = preg_replace('/[^a-zA-Z0-9_-]/', '', $selectedPeriod);
    header('Content-Type: text/csv; charset=UTF-8');
    header('Content-Disposition: attachment; filename="ars-estadistiques-' . $safePeriod . '.csv"');
    echo "\xEF\xBB\xBF";
    $out = fopen('php://output', 'w');
    $periodTitle = $selectedPeriod === 'all' ? 'Històric total' : $formatMonth($selectedPeriod);
    fputcsv($out, ['ARS Advocats i Assessors — Informe Estadístic', $periodTitle, 'Generat: ' . date('d/m/Y H:i')], ';');
    fputcsv($out, [], ';');
    fputcsv($out, ['SECCIÓ', 'MÈTRICA', 'VALOR'], ';');
    fputcsv($out, ['Visites', 'Total visites web', $vTotal], ';');
    fputcsv($out, ['Visites', 'Buscadors clàssics (Google, Bing...)', $vGoogle], ';');
    fputcsv($out, ['Visites', 'Buscadors i Assistents IA (total)', $vAi], ';');
    fputcsv($out, ['Visites IA', 'ChatGPT', $aiChatgpt], ';');
    fputcsv($out, ['Visites IA', 'Perplexity', $aiPerplexity], ';');
    fputcsv($out, ['Visites IA', 'Gemini', $aiGemini], ';');
    fputcsv($out, ['Visites IA', 'Claude', $aiClaude], ';');
    fputcsv($out, ['Visites IA', 'Altres IA', $aiOther], ';');
    fputcsv($out, ['Visites', 'Xarxes socials i directoris', $vSocial], ';');
    fputcsv($out, ['Visites', 'Directe / Apps / Altres', $vDirect], ';');
    fputcsv($out, ['Assistent IA', 'Obertures del xat', $chatOpen], ';');
    fputcsv($out, ['Assistent IA', 'Converses iniciades', $chatSessions], ';');
    fputcsv($out, ['Assistent IA', 'Consultes (missatges) enviades', $chatMsg], ';');
    fputcsv($out, ['Assistent IA', 'Pas a WhatsApp des del xat', $chatToWa], ';');
    fputcsv($out, ['Assistent IA', 'Pas al Formulari des del xat', $chatToForm], ';');
    fputcsv($out, ['Contactes', 'Total contactes generats', $totalLeads], ';');
    fputcsv($out, ['Contactes', 'WhatsApp total (Xat + Web)', $totalWa], ';');
    fputcsv($out, ['Contactes', 'WhatsApp web directe', $webWa], ';');
    fputcsv($out, ['Contactes', 'Clics a Telèfon (tel:)', $webTel], ';');
    fputcsv($out, ['Contactes', 'Clics a Email (mailto:)', $webMailto], ';');
    fputcsv($out, ['Contactes', 'Formularis enviats (total)', $totalForm], ';');
    fputcsv($out, ['Contactes', 'Formularis via Chatbot', $webFormFromChat], ';');
    fputcsv($out, ['Contactes', 'Formularis web directes', $webFormDirect], ';');
    fputcsv($out, ['Idiomes', 'Català', $langCa], ';');
    fputcsv($out, ['Idiomes', 'Castellà', $langEs], ';');
    fputcsv($out, ['Idiomes', 'Anglès', $langEn], ';');
    foreach ($AREA_LABELS as $aKey => $aLabel) {
        $c = $val($aKey);
        if ($c > 0) {
            fputcsv($out, ['Temàtica consultada', $aLabel, $c], ';');
        }
    }
    fputcsv($out, [], ';');
    fputcsv($out, ['DESGLOSSAMENT DIARI (ÚLTIMS 30 DIES)'], ';');
    fputcsv($out, ['Data', 'Visites', 'Google', 'IA', 'Converses Xat', 'Consultes Xat', 'WhatsApp', 'Telèfon', 'Email', 'Formularis', 'Total Contactes'], ';');
    foreach ($chartPayload['days30'] as $r) {
        fputcsv($out, [$r['fullLabel'], $r['visits'], $r['google'], $r['ai'], $r['sessions'], $r['chat'], $r['wa'], $r['tel'], $r['mailto'], $r['form'], $r['leads']], ';');
    }
    fclose($out);
    exit;
}
?>
<!DOCTYPE html>
<html lang="ca">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="robots" content="noindex, nofollow, noarchive">
  <title>Estadístiques Web & Assistent | ARS Advocats i Assessors</title>
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #fbf7f6;
      --surface: #ffffff;
      --surface-soft: #f5eeed;
      --accent: #c10c13;
      --accent-dark: #7a070c;
      --accent-deep: #540307;
      --accent-soft: #dda09f;
      --text-main: #1c1314;
      --text-body: #3c3233;
      --text-muted: #6e6061;
      --border: rgba(40, 20, 20, 0.09);
      --shadow: 0 10px 30px rgba(40, 10, 15, 0.06);
      --serif: "Cormorant Garamond", Georgia, serif;
      --sans: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: var(--sans);
      background: var(--bg);
      color: var(--text-main);
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
      padding-bottom: 48px;
    }

    /* Top Brand Bar */
    .topbar {
      background: linear-gradient(135deg, #1c1314 0%, #540307 100%);
      color: #ffffff;
      padding: 20px 20px 24px;
      border-bottom: 3px solid var(--accent);
    }

    .wrap {
      max-width: 1120px;
      margin: 0 auto;
      padding: 0 18px;
    }

    .topbar-inner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .brand-mark {
      width: 44px;
      height: 44px;
      border-radius: 10px;
      background: #ffffff;
      padding: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.25);
      flex-shrink: 0;
    }

    .brand-mark img {
      width: 100%;
      height: 100%;
      object-fit: contain;
      display: block;
    }

    .brand h1 {
      font-family: var(--sans);
      font-size: clamp(1.15rem, 2.5vw, 1.45rem);
      font-weight: 700;
      line-height: 1.15;
      letter-spacing: -0.015em;
    }

    .brand-sub {
      font-size: 0.78rem;
      color: rgba(255,255,255,0.75);
      margin-top: 3px;
    }

    .meta-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 7px 13px;
      border-radius: 9999px;
      background: rgba(255,255,255,0.1);
      border: 1px solid rgba(255,255,255,0.18);
      font-size: 0.75rem;
      color: rgba(255,255,255,0.9);
      white-space: nowrap;
    }

    .meta-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #4ade80;
    }

    /* Period Filter Bar */
    .period-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
      margin: 22px 0 20px;
    }

    .period-pills {
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      padding-bottom: 4px;
      -webkit-overflow-scrolling: touch;
      max-width: 100%;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      padding: 7px 14px;
      border-radius: 9999px;
      font-size: 0.8rem;
      font-weight: 600;
      text-decoration: none;
      color: var(--text-body);
      background: var(--surface);
      border: 1px solid var(--border);
      white-space: nowrap;
      transition: all 0.2s ease;
    }

    .pill:hover {
      border-color: var(--accent);
      color: var(--accent);
    }

    .pill.active {
      background: var(--accent);
      color: #ffffff;
      border-color: var(--accent);
      box-shadow: 0 4px 12px rgba(193, 12, 19, 0.22);
    }

    .period-actions {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }

    .refresh-link {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-family: inherit;
      font-size: 0.78rem;
      font-weight: 600;
      color: var(--accent-dark);
      text-decoration: none;
      padding: 6px 11px;
      border-radius: 8px;
      background: var(--surface-soft);
      border: 1px solid var(--border);
      cursor: pointer;
      transition: background 0.18s ease, border-color 0.18s ease;
    }

    .refresh-link:hover {
      background: #efe3e2;
      border-color: var(--accent);
    }

    .empty-hint {
      font-size: 0.8rem;
      color: var(--text-muted);
      background: var(--bg);
      border: 1px dashed var(--border);
      border-radius: 10px;
      padding: 14px;
      line-height: 1.45;
    }

    /* KPI Grid */
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin-bottom: 20px;
    }

    .kpi-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-top: 3px solid var(--accent-soft);
      border-radius: 12px;
      padding: 18px 18px 16px;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      gap: 6px;
    }

    .kpi-card--primary {
      border-top-color: var(--accent);
    }

    .kpi-label {
      font-size: 0.74rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-muted);
    }

    .kpi-value {
      font-size: clamp(1.85rem, 3.5vw, 2.35rem);
      font-weight: 700;
      color: var(--text-main);
      font-variant-numeric: tabular-nums;
      line-height: 1.1;
    }

    .kpi-sub {
      font-size: 0.76rem;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .kpi-sub strong {
      color: var(--accent-dark);
      font-weight: 600;
    }

    /* Two-column dashboard layout */
    .panels-grid {
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 16px;
      margin-bottom: 16px;
    }

    .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      box-shadow: var(--shadow);
      min-width: 0;
      overflow: hidden;
    }

    .panel-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 16px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 12px;
    }

    .panel-title {
      font-family: var(--sans);
      font-size: 1.05rem;
      font-weight: 700;
      letter-spacing: -0.015em;
      color: var(--text-main);
    }

    .panel-badge {
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--accent-dark);
      background: var(--surface-soft);
      padding: 3px 9px;
      border-radius: 9999px;
      white-space: nowrap;
    }

    /* Progress Bars */
    .metric-list {
      display: flex;
      flex-direction: column;
      gap: 14px;
    }

    .metric-row-top {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 8px;
      font-size: 0.84rem;
      margin-bottom: 6px;
    }

    .metric-name {
      font-weight: 600;
      color: var(--text-main);
    }

    .metric-num {
      font-variant-numeric: tabular-nums;
      font-weight: 700;
      color: var(--text-main);
      white-space: nowrap;
    }

    .metric-num span {
      font-weight: 500;
      color: var(--text-muted);
      font-size: 0.76rem;
      margin-left: 4px;
    }

    .bar-track {
      height: 9px;
      background: var(--surface-soft);
      border-radius: 9999px;
      overflow: hidden;
    }

    .bar-fill {
      height: 100%;
      border-radius: 9999px;
      background: linear-gradient(90deg, var(--accent) 0%, var(--accent-dark) 100%);
      transition: width 0.5s ease;
    }

    .bar-fill--ai {
      background: linear-gradient(90deg, #1c1314 0%, #7a070c 100%);
    }

    .bar-fill--soft {
      background: #c78b8a;
    }

    .bar-fill--muted {
      background: #b5a6a7;
    }

    /* AI Engine Chips */
    .ai-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
    }

    .ai-chip {
      font-size: 0.71rem;
      font-weight: 600;
      padding: 3px 9px;
      border-radius: 9999px;
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text-body);
      font-variant-numeric: tabular-nums;
    }

    /* Split Comparison Box */
    .split-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px dashed var(--border);
    }

    .split-box {
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
    }

    .split-box-title {
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .split-box-val {
      font-size: 1.3rem;
      font-weight: 700;
      margin: 4px 0 2px;
      font-variant-numeric: tabular-nums;
    }

    .split-box-detail {
      font-size: 0.74rem;
      color: var(--text-muted);
    }

    /* 14-day Chart */
    .chart-scroll {
      overflow-x: auto;
      padding-bottom: 4px;
      -webkit-overflow-scrolling: touch;
    }

    .chart-bars {
      display: grid;
      grid-template-columns: repeat(14, minmax(36px, 1fr));
      gap: 8px;
      align-items: end;
      height: 150px;
      padding-top: 16px;
    }

    .day-col {
      display: flex;
      flex-direction: column;
      align-items: center;
      height: 100%;
      justify-content: flex-end;
      gap: 6px;
    }

    .day-stack {
      width: 100%;
      height: 112px;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      gap: 3px;
    }

    .vbar {
      width: 9px;
      min-height: 3px;
      border-radius: 4px 4px 1px 1px;
    }

    .vbar--visits { background: #d9b8b7; }
    .vbar--chat   { background: var(--accent); }
    .vbar--leads  { background: #1c1314; }

    .day-label {
      font-size: 0.68rem;
      color: var(--text-muted);
      font-variant-numeric: tabular-nums;
    }

    .chart-legend {
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      margin-top: 12px;
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    .legend-item {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .legend-dot {
      width: 9px;
      height: 9px;
      border-radius: 3px;
    }

    /* Interactive Monthly / Yearly SVG Chart */
    .evo-panel {
      margin-bottom: 16px;
    }

    .evo-controls {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      max-width: 100%;
    }

    .seg-tabs {
      display: inline-flex;
      background: var(--surface-soft);
      border: 1px solid var(--border);
      border-radius: 9999px;
      padding: 3px;
      gap: 2px;
      max-width: 100%;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
    }

    .seg-tabs::-webkit-scrollbar {
      display: none;
    }

    .seg-btn {
      border: none;
      background: transparent;
      color: var(--text-muted);
      font-family: inherit;
      font-size: 0.74rem;
      font-weight: 600;
      padding: 5px 11px;
      border-radius: 9999px;
      white-space: nowrap;
      flex-shrink: 0;
      cursor: pointer;
      transition: all 0.18s ease;
    }

    .seg-btn.active {
      background: var(--accent);
      color: #ffffff;
      box-shadow: 0 2px 8px rgba(193, 12, 19, 0.22);
    }

    .evo-subcontrols {
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }

    .zoom-group {
      display: inline-flex;
      align-items: center;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 9999px;
      padding: 2px;
    }

    .zoom-btn {
      width: 26px;
      height: 26px;
      border: none;
      border-radius: 50%;
      background: transparent;
      color: var(--text-main);
      font-family: inherit;
      font-size: 0.9rem;
      font-weight: 700;
      line-height: 1;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s ease, color 0.15s ease;
    }

    .zoom-btn:hover {
      background: var(--surface-soft);
      color: var(--accent);
    }

    .zoom-label {
      font-size: 0.68rem;
      font-weight: 600;
      color: var(--text-muted);
      padding: 0 4px;
      min-width: 34px;
      text-align: center;
      font-variant-numeric: tabular-nums;
    }

    .year-select {
      font-family: inherit;
      font-size: 0.76rem;
      font-weight: 600;
      color: var(--text-main);
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 9999px;
      padding: 5px 11px;
      cursor: pointer;
      outline: none;
    }

    .year-select:focus {
      border-color: var(--accent);
    }

    .evo-stage {
      position: relative;
      width: 100%;
      min-width: 0;
    }

    .evo-scroll {
      width: 100%;
      max-width: 100%;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      padding-bottom: 6px;
    }

    .evo-svg {
      display: block;
      width: 100%;
      min-width: 560px;
      height: 235px;
      overflow: visible;
    }

    .evo-hint {
      font-size: 0.7rem;
      color: var(--text-muted);
      margin-top: 2px;
      display: none;
    }

    @media (max-width: 640px) {
      .evo-controls {
        width: 100%;
        justify-content: space-between;
      }
      .evo-hint {
        display: block;
      }
    }

    .evo-grid-line {
      stroke: rgba(40, 20, 20, 0.08);
      stroke-dasharray: 3 4;
    }

    .evo-axis-text {
      font-family: var(--sans);
      font-size: 11px;
      fill: var(--text-muted);
      font-variant-numeric: tabular-nums;
    }

    .evo-val-text {
      font-family: var(--sans);
      font-size: 10px;
      font-weight: 700;
      fill: var(--text-main);
      font-variant-numeric: tabular-nums;
    }

    .evo-bar {
      transition: opacity 0.18s ease;
    }

    .evo-hit {
      fill: transparent;
      cursor: pointer;
    }

    .evo-hit:hover ~ .evo-bar,
    .evo-col.is-active .evo-bar {
      opacity: 1;
    }

    .evo-col.is-active .evo-col-bg {
      fill: rgba(193, 12, 19, 0.05);
    }

    .evo-tooltip {
      margin-top: 12px;
      padding: 11px 14px;
      background: var(--bg);
      border: 1px solid var(--border);
      border-left: 3px solid var(--accent);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
      font-size: 0.78rem;
      color: var(--text-body);
    }

    .evo-tooltip strong {
      color: var(--text-main);
      font-weight: 700;
    }

    .evo-tooltip-metrics {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      font-variant-numeric: tabular-nums;
    }

    .legend-toggle {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border: 1px solid var(--border);
      background: var(--surface);
      padding: 5px 10px;
      border-radius: 9999px;
      font-family: inherit;
      font-size: 0.74rem;
      font-weight: 600;
      color: var(--text-body);
      cursor: pointer;
      transition: all 0.18s ease;
    }

    .legend-toggle.is-off {
      opacity: 0.42;
      text-decoration: line-through;
    }

    .footer-note {
      margin-top: 22px;
      text-align: center;
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    /* Responsive Mobile */
    @media (max-width: 860px) {
      .kpi-grid {
        grid-template-columns: repeat(2, 1fr);
      }
      .panels-grid {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 480px) {
      .topbar { padding: 16px 0 18px; }
      .wrap { padding: 0 14px; }
      .kpi-grid { gap: 10px; }
      .kpi-card { padding: 14px; }
      .panel { padding: 16px; }
      .split-grid { grid-template-columns: 1fr; }
    }

    @media print {
      @page {
        size: A4 portrait;
        margin: 12mm;
      }
      body {
        background: #ffffff;
        padding-bottom: 0;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
      .topbar {
        border-radius: 10px;
        margin-bottom: 14px;
      }
      .period-bar,
      .evo-controls,
      .evo-hint,
      .chart-legend {
        display: none !important;
      }
      .kpi-grid {
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 10px;
      }
      .panels-grid {
        grid-template-columns: 1fr 1fr !important;
        gap: 12px;
      }
      .kpi-card,
      .panel {
        box-shadow: none !important;
        break-inside: avoid;
        page-break-inside: avoid;
      }
      .evo-scroll {
        overflow: visible !important;
      }
      .evo-svg {
        min-width: 0 !important;
        width: 100% !important;
      }
    }
  </style>
</head>
<body>
  <header class="topbar">
    <div class="wrap topbar-inner">
      <div class="brand">
        <div class="brand-mark">
          <img src="/assets/images/apple-touch-icon.png" alt="ARS Advocats">
        </div>
        <div>
          <h1>ARS Advocats · Estadístiques</h1>
          <div class="brand-sub">Rendiment web, Assistent IA i captació de consultes</div>
        </div>
      </div>
      <div class="meta-pill">
        <span class="meta-dot"></span>
        <span>Actualitzat: <?= htmlspecialchars($updatedLabel, ENT_QUOTES, 'UTF-8') ?></span>
      </div>
    </div>
  </header>

  <main class="wrap">
    <div class="period-bar">
      <nav class="period-pills" aria-label="Selector de període">
        <a href="<?= htmlspecialchars($buildUrl('all'), ENT_QUOTES, 'UTF-8') ?>" class="pill <?= $selectedPeriod === 'all' ? 'active' : '' ?>">Històric total</a>
        <?php foreach ($availableMonths as $ym): ?>
          <a href="<?= htmlspecialchars($buildUrl($ym), ENT_QUOTES, 'UTF-8') ?>" class="pill <?= $selectedPeriod === $ym ? 'active' : '' ?>">
            <?= htmlspecialchars($formatMonth($ym), ENT_QUOTES, 'UTF-8') ?>
          </a>
        <?php endforeach; ?>
      </nav>
      <div class="period-actions">
        <a href="<?= htmlspecialchars($buildUrl($selectedPeriod, 'export=csv'), ENT_QUOTES, 'UTF-8') ?>" class="refresh-link">↓ Exportar CSV</a>
        <button type="button" class="refresh-link" onclick="window.print()">⎙ Imprimir / PDF</button>
        <a href="<?= htmlspecialchars($buildUrl($selectedPeriod), ENT_QUOTES, 'UTF-8') ?>" class="refresh-link">↻ Actualitzar</a>
      </div>
    </div>

    <!-- 4 Hero KPIs -->
    <section class="kpi-grid">
      <article class="kpi-card kpi-card--primary">
        <div class="kpi-label">Visites web</div>
        <div class="kpi-value"><?= number_format($vTotal, 0, ',', '.') ?></div>
        <div class="kpi-sub">Google: <strong><?= $vGoogle ?></strong> · IA: <strong><?= $vAi ?></strong></div>
      </article>

      <article class="kpi-card kpi-card--primary">
        <div class="kpi-label">Consultes al Chatbot</div>
        <div class="kpi-value"><?= number_format($chatMsg, 0, ',', '.') ?></div>
        <div class="kpi-sub">Converses: <strong><?= $chatSessions ?></strong> · Obertures: <strong><?= $chatOpen ?></strong></div>
      </article>

      <article class="kpi-card">
        <div class="kpi-label">Contactes directes</div>
        <div class="kpi-value"><?= number_format($totalDirectC, 0, ',', '.') ?></div>
        <div class="kpi-sub">WA: <strong><?= $totalWa ?></strong> · Tel: <strong><?= $webTel ?></strong> · Email: <strong><?= $webMailto ?></strong></div>
      </article>

      <article class="kpi-card">
        <div class="kpi-label">Formularis enviats</div>
        <div class="kpi-value"><?= number_format($totalForm, 0, ',', '.') ?></div>
        <div class="kpi-sub">Via Chatbot: <strong><?= $webFormFromChat ?></strong> · Directes: <strong><?= $webFormDirect ?></strong></div>
      </article>
    </section>

    <!-- Interactive Temporal Evolution Chart (7d / 30d / Months / Quarters / Years) -->
    <section class="panel evo-panel" id="evoChartPanel">
      <div class="panel-head">
        <div>
          <h2 class="panel-title">Evolució temporal</h2>
        </div>
        <div class="evo-controls">
          <div class="seg-tabs" role="tablist" aria-label="Selector de temporalitat">
            <button type="button" class="seg-btn" data-evo-mode="days7" role="tab" aria-selected="false">7 dies</button>
            <button type="button" class="seg-btn active" data-evo-mode="days30" role="tab" aria-selected="true">30 dies</button>
            <button type="button" class="seg-btn" data-evo-mode="monthly" role="tab" aria-selected="false">Mesos</button>
            <button type="button" class="seg-btn" data-evo-mode="quarterly" role="tab" aria-selected="false">Trimestres</button>
            <button type="button" class="seg-btn" data-evo-mode="yearly" role="tab" aria-selected="false">Anys</button>
          </div>
          <div class="evo-subcontrols">
            <select id="evoYearSelect" class="year-select" aria-label="Seleccionar any" style="display:none"></select>
            <div class="zoom-group" aria-label="Zoom del gràfic">
              <button type="button" class="zoom-btn" id="evoZoomOut" title="Reduir">−</button>
              <span class="zoom-label" id="evoZoomLabel">100%</span>
              <button type="button" class="zoom-btn" id="evoZoomIn" title="Augmentar">+</button>
            </div>
          </div>
        </div>
      </div>

      <div class="evo-stage">
        <div class="evo-scroll" id="evoScroll">
          <svg id="evoSvg" class="evo-svg" viewBox="0 0 760 240" preserveAspectRatio="none" role="img" aria-label="Gràfic evolutiu per temporalitat"></svg>
        </div>
        <div class="evo-hint">← Llisca cap a l'esquerra per veure dates anteriors</div>
        <div class="evo-tooltip" id="evoTooltip">
          <span>Toca o passa el cursor sobre una barra per veure'n el detall.</span>
        </div>
      </div>

      <div class="chart-legend" id="evoLegend">
        <button type="button" class="legend-toggle" data-series="visits">
          <span class="legend-dot" style="background:#d9b8b7"></span> Visites
        </button>
        <button type="button" class="legend-toggle" data-series="chat">
          <span class="legend-dot" style="background:#c10c13"></span> Consultes Chatbot
        </button>
        <button type="button" class="legend-toggle" data-series="leads">
          <span class="legend-dot" style="background:#1c1314"></span> Contactes (WA · Form · Tel · Email)
        </button>
      </div>
    </section>

    <!-- Main Breakdown Panels -->
    <section class="panels-grid">
      <!-- Left: Chatbot Funnel & Conversions -->
      <article class="panel">
        <div class="panel-head">
          <h2 class="panel-title">Rendiment de l'Assistent IA</h2>
          <span class="panel-badge">Conversió: <?= $chatConvRate ?>% (sobre <?= $chatConvBaseLabel ?>)</span>
        </div>

        <div class="metric-list">
          <div>
            <div class="metric-row-top">
              <span class="metric-name">1. Obertures de la finestra del xat</span>
              <span class="metric-num"><?= $chatOpen ?></span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width: <?= $chatOpen > 0 ? 100 : 0 ?>%"></div></div>
          </div>

          <div>
            <div class="metric-row-top">
              <span class="metric-name">2. Converses iniciades (sessions úniques)</span>
              <span class="metric-num"><?= $chatSessions ?> <?php if ($chatOpen > 0): ?><span>(<?= min(100, $pct($chatSessions, $chatOpen)) ?>%)</span><?php endif; ?></span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width: <?= $chatSessions > 0 ? min(100, $pct($chatSessions, max($chatOpen, $chatSessions))) : 0 ?>%"></div></div>
          </div>

          <div>
            <div class="metric-row-top">
              <span class="metric-name">3. Consultes (missatges) enviades a la IA</span>
              <span class="metric-num"><?= $chatMsg ?></span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width: <?= $chatMsg > 0 ? 100 : 0 ?>%"></div></div>
          </div>

          <div>
            <div class="metric-row-top">
              <span class="metric-name">4. Pas a WhatsApp des del xat</span>
              <span class="metric-num"><?= $chatToWa ?> <span>(<?= $pct($chatToWa, $chatConvBase) ?>%)</span></span>
            </div>
            <div class="bar-track"><div class="bar-fill bar-fill--ai" style="width: <?= min(100, $pct($chatToWa, max(1, $chatConvBase))) ?>%"></div></div>
          </div>

          <div>
            <div class="metric-row-top">
              <span class="metric-name">5. Pas al Formulari des del xat</span>
              <span class="metric-num"><?= $chatToForm ?> <span>(<?= $pct($chatToForm, $chatConvBase) ?>%)</span></span>
            </div>
            <div class="bar-track"><div class="bar-fill bar-fill--soft" style="width: <?= min(100, $pct($chatToForm, max(1, $chatConvBase))) ?>%"></div></div>
          </div>
        </div>

        <div class="split-grid">
          <div class="split-box">
            <div class="split-box-title">Total contactes generats</div>
            <div class="split-box-val"><?= $totalLeads ?></div>
            <div class="split-box-detail"><?= $totalWa ?> WA · <?= $totalForm ?> Form · <?= $webTel ?> Tel · <?= $webMailto ?> Email</div>
          </div>
          <div class="split-box">
            <div class="split-box-title">Origen dels contactes</div>
            <div class="split-box-val"><?= $pct($chatToWa + $webFormFromChat, $totalLeads) ?>% xat</div>
            <div class="split-box-detail"><?= $chatToWa + $webFormFromChat ?> via Chatbot · <?= $webWa + $webFormDirect + $webTel + $webMailto ?> web directe</div>
          </div>
        </div>
      </article>

      <!-- Right: Traffic Sources (Google vs AI Search) -->
      <article class="panel">
        <div class="panel-head">
          <h2 class="panel-title">Origen de les visites</h2>
          <span class="panel-badge">1 vegada per sessió</span>
        </div>

        <div class="metric-list">
          <div>
            <div class="metric-row-top">
              <span class="metric-name">Buscadors clàssics (Google, Bing...)</span>
              <span class="metric-num"><?= $vGoogle ?> <span>(<?= $pct($vGoogle, $vTotal) ?>%)</span></span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width: <?= $pct($vGoogle, $vTotal) ?>%"></div></div>
          </div>

          <div>
            <div class="metric-row-top">
              <span class="metric-name">Buscadors i Assistents IA</span>
              <span class="metric-num"><?= $vAi ?> <span>(<?= $pct($vAi, $vTotal) ?>%)</span></span>
            </div>
            <div class="bar-track"><div class="bar-fill bar-fill--ai" style="width: <?= $pct($vAi, $vTotal) ?>%"></div></div>
            <div class="ai-chips">
              <span class="ai-chip">ChatGPT: <?= $aiChatgpt ?></span>
              <span class="ai-chip">Perplexity: <?= $aiPerplexity ?></span>
              <span class="ai-chip">Gemini: <?= $aiGemini ?></span>
              <span class="ai-chip">Claude: <?= $aiClaude ?></span>
              <?php if ($aiOther > 0): ?><span class="ai-chip">Altres IA: <?= $aiOther ?></span><?php endif; ?>
            </div>
          </div>

          <div>
            <div class="metric-row-top">
              <span class="metric-name">Xarxes socials i directoris</span>
              <span class="metric-num"><?= $vSocial ?> <span>(<?= $pct($vSocial, $vTotal) ?>%)</span></span>
            </div>
            <div class="bar-track"><div class="bar-fill bar-fill--soft" style="width: <?= $pct($vSocial, $vTotal) ?>%"></div></div>
          </div>

          <div>
            <div class="metric-row-top">
              <span class="metric-name">Directe / Apps / Altres</span>
              <span class="metric-num"><?= $vDirect ?> <span>(<?= $pct($vDirect, $vTotal) ?>%)</span></span>
            </div>
            <div class="bar-track"><div class="bar-fill bar-fill--muted" style="width: <?= $pct($vDirect, $vTotal) ?>%"></div></div>
          </div>
        </div>
      </article>
    </section>

    <!-- Topics, Languages & Direct Contact Channels -->
    <section class="panels-grid">
      <!-- Left: Top Consulted Legal Areas -->
      <article class="panel">
        <div class="panel-head">
          <h2 class="panel-title">Temàtiques consultades</h2>
          <span class="panel-badge">Xat i Formulari · Anònim</span>
        </div>

        <?php if (!empty($areaCounts)): ?>
          <div class="metric-list">
            <?php foreach (array_slice($areaCounts, 0, 8, true) as $aKey => $aCount): ?>
              <div>
                <div class="metric-row-top">
                  <span class="metric-name"><?= htmlspecialchars($AREA_LABELS[$aKey] ?? $aKey, ENT_QUOTES, 'UTF-8') ?></span>
                  <span class="metric-num"><?= $aCount ?> <span>(<?= $pct($aCount, $areaTotal) ?>%)</span></span>
                </div>
                <div class="bar-track"><div class="bar-fill" style="width: <?= $pct($aCount, $areaTotal) ?>%"></div></div>
              </div>
            <?php endforeach; ?>
          </div>
        <?php else: ?>
          <div class="empty-hint">
            Les àrees jurídiques consultades (Família, Laboral, Herències, Penal, etc.) s'aniran registrant automàticament de forma anònima a partir de les pròximes converses i formularis.
          </div>
        <?php endif; ?>
      </article>

      <!-- Right: Languages & Direct Contact Channels -->
      <article class="panel">
        <div class="panel-head">
          <h2 class="panel-title">Idiomes i canals de contacte</h2>
          <span class="panel-badge"><?= $totalLeads ?> contactes</span>
        </div>

        <div class="metric-list">
          <div>
            <div class="metric-row-top">
              <span class="metric-name">WhatsApp (Xat + Web)</span>
              <span class="metric-num"><?= $totalWa ?> <span>(<?= $pct($totalWa, $totalLeads) ?>%)</span></span>
            </div>
            <div class="bar-track"><div class="bar-fill" style="width: <?= $pct($totalWa, $totalLeads) ?>%"></div></div>
          </div>

          <div>
            <div class="metric-row-top">
              <span class="metric-name">Formularis enviats</span>
              <span class="metric-num"><?= $totalForm ?> <span>(<?= $pct($totalForm, $totalLeads) ?>%)</span></span>
            </div>
            <div class="bar-track"><div class="bar-fill bar-fill--ai" style="width: <?= $pct($totalForm, $totalLeads) ?>%"></div></div>
          </div>

          <div>
            <div class="metric-row-top">
              <span class="metric-name">Clics a Telèfon (938 795 876)</span>
              <span class="metric-num"><?= $webTel ?> <span>(<?= $pct($webTel, $totalLeads) ?>%)</span></span>
            </div>
            <div class="bar-track"><div class="bar-fill bar-fill--soft" style="width: <?= $pct($webTel, $totalLeads) ?>%"></div></div>
          </div>

          <div>
            <div class="metric-row-top">
              <span class="metric-name">Clics a Email (info@arsadvocats.com)</span>
              <span class="metric-num"><?= $webMailto ?> <span>(<?= $pct($webMailto, $totalLeads) ?>%)</span></span>
            </div>
            <div class="bar-track"><div class="bar-fill bar-fill--muted" style="width: <?= $pct($webMailto, $totalLeads) ?>%"></div></div>
          </div>
        </div>

        <div class="split-grid" style="grid-template-columns: 1fr; margin-top: 16px;">
          <div class="split-box">
            <div class="split-box-title">Idioma de les consultes (<?= $langTotal ?> registrades)</div>
            <div class="ai-chips" style="margin-top: 8px;">
              <span class="ai-chip">Català: <strong><?= $langCa ?></strong><?php if ($langTotal > 0): ?> (<?= $pct($langCa, $langTotal) ?>%)<?php endif; ?></span>
              <span class="ai-chip">Castellà: <strong><?= $langEs ?></strong><?php if ($langTotal > 0): ?> (<?= $pct($langEs, $langTotal) ?>%)<?php endif; ?></span>
              <span class="ai-chip">Anglès: <strong><?= $langEn ?></strong><?php if ($langTotal > 0): ?> (<?= $pct($langEn, $langTotal) ?>%)<?php endif; ?></span>
            </div>
          </div>
        </div>
      </article>
    </section>

    <p class="footer-note">
      ARS Advocats i Assessors Granollers, S.C.P. · Panell privat no indexat · Dades 100% anònimes sense cookies ni textos de converses.
    </p>
  </main>

  <script>
    (function () {
      const DATA = <?= json_encode($chartPayload, JSON_UNESCAPED_UNICODE) ?>;
      const svg = document.getElementById('evoSvg');
      const evoScroll = document.getElementById('evoScroll');
      const yearSelect = document.getElementById('evoYearSelect');
      const tooltip = document.getElementById('evoTooltip');
      const zoomOutBtn = document.getElementById('evoZoomOut');
      const zoomInBtn = document.getElementById('evoZoomIn');
      const zoomLabel = document.getElementById('evoZoomLabel');
      const modeBtns = document.querySelectorAll('[data-evo-mode]');
      const legendBtns = document.querySelectorAll('[data-series]');

      if (!svg || !DATA) return;

      let mode = 'days30';
      let selectedYear = DATA.currentYear;
      const zoomSteps = [0.7, 1, 1.4, 1.8, 2.3];
      let zoomIdx = 1;
      const visible = { visits: true, chat: true, leads: true };

      function applyZoom(scrollToRight) {
        const z = zoomSteps[zoomIdx];
        const baseW = mode === 'days30' ? 760 : (mode === 'monthly' ? 600 : 460);
        const targetW = Math.round(baseW * z);
        svg.style.minWidth = (z <= 0.75 ? 0 : targetW) + 'px';
        svg.style.width = z > 1 ? targetW + 'px' : '100%';
        if (zoomLabel) zoomLabel.textContent = Math.round(z * 100) + '%';
        if (scrollToRight && evoScroll) {
          requestAnimationFrame(() => {
            evoScroll.scrollLeft = evoScroll.scrollWidth;
          });
        }
      }

      DATA.years.forEach((yr) => {
        const opt = document.createElement('option');
        opt.value = yr;
        opt.textContent = yr;
        if (yr === selectedYear) opt.selected = true;
        yearSelect.appendChild(opt);
      });

      function setTooltip(row) {
        if (!row) return;
        const sessTxt = row.sessions > 0 ? ` (${row.sessions} conv.)` : '';
        const extraC = (row.tel > 0 || row.mailto > 0) ? ` · Tel ${row.tel} · Mail ${row.mailto}` : '';
        tooltip.innerHTML = `
          <strong>${row.fullLabel}</strong>
          <div class="evo-tooltip-metrics">
            <span>Visites: <strong>${row.visits}</strong> (Google ${row.google} · IA ${row.ai})</span>
            <span>Chatbot: <strong>${row.chat}</strong>${sessTxt}</span>
            <span>Contactes: <strong>${row.leads}</strong> (WA ${row.wa} · Form ${row.form}${extraC})</span>
          </div>
        `;
      }

      function render() {
        let rows = [];
        if (mode === 'days7') rows = DATA.days7 || [];
        else if (mode === 'days30') rows = DATA.days30 || [];
        else if (mode === 'quarterly') rows = DATA.quarterlyByYear[selectedYear] || [];
        else if (mode === 'yearly') rows = DATA.yearly || [];
        else rows = DATA.monthlyByYear[selectedYear] || [];

        yearSelect.style.display = (mode === 'monthly' || mode === 'quarterly') ? 'inline-block' : 'none';

        const activeSeries = ['visits', 'chat', 'leads'].filter((s) => visible[s]);
        const colors = { visits: '#d9b8b7', chat: '#c10c13', leads: '#1c1314' };

        let maxVal = 1;
        rows.forEach((r) => {
          activeSeries.forEach((s) => {
            if (r[s] > maxVal) maxVal = r[s];
          });
        });

        // Round nice Y-axis ceiling
        const niceMax = maxVal <= 4 ? 4 : Math.ceil(maxVal / 4) * 4;

        const W = 760;
        const H = 240;
        const padL = 36;
        const padR = 14;
        const padT = 18;
        const padB = 30;
        const plotW = W - padL - padR;
        const plotH = H - padT - padB;

        const n = Math.max(1, rows.length);
        const colW = plotW / n;
        const barGap = n > 20 ? 1.5 : 3;
        const groupW = Math.min(colW * 0.72, activeSeries.length * 16 + 8);
        const barW = activeSeries.length > 0
          ? Math.max(3.5, Math.min(20, (groupW - barGap * (activeSeries.length - 1)) / activeSeries.length))
          : 10;

        let out = '';

        // Gridlines & Y labels (4 steps)
        for (let i = 0; i <= 4; i++) {
          const val = Math.round((niceMax / 4) * i);
          const y = padT + plotH - (plotH * i) / 4;
          out += `<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W - padR}" y2="${y.toFixed(1)}" class="evo-grid-line" />`;
          out += `<text x="${padL - 8}" y="${(y + 4).toFixed(1)}" text-anchor="end" class="evo-axis-text">${val}</text>`;
        }

        // Columns + bars
        const trendPoints = [];
        rows.forEach((r, idx) => {
          const cx = padL + colW * idx + colW / 2;
          const totalGroupW = activeSeries.length * barW + Math.max(0, activeSeries.length - 1) * barGap;
          const startX = cx - totalGroupW / 2;

          out += `<g class="evo-col" data-idx="${idx}">`;
          out += `<rect class="evo-col-bg" x="${(padL + colW * idx + 2).toFixed(1)}" y="${padT}" width="${(colW - 4).toFixed(1)}" height="${plotH}" rx="6" fill="transparent" />`;

          activeSeries.forEach((s, si) => {
            const v = r[s] || 0;
            const h = v > 0 ? Math.max(4, (v / niceMax) * plotH) : 2;
            const x = startX + si * (barW + barGap);
            const y = padT + plotH - h;
            out += `<rect class="evo-bar" x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${barW.toFixed(1)}" height="${h.toFixed(1)}" rx="3" fill="${colors[s]}" opacity="${v > 0 ? '0.92' : '0.28'}" />`;
            if ((mode === 'yearly' || mode === 'quarterly') && v > 0) {
              out += `<text x="${(x + barW / 2).toFixed(1)}" y="${(y - 5).toFixed(1)}" text-anchor="middle" class="evo-val-text">${v}</text>`;
            }
          });

          if (visible.leads) {
            const ly = padT + plotH - ((r.leads || 0) / niceMax) * plotH;
            trendPoints.push(`${cx.toFixed(1)},${ly.toFixed(1)}`);
          }

          const showXLabel = (n <= 15) || (idx % 5 === 0) || (idx === n - 1);
          if (showXLabel) {
            out += `<text x="${cx.toFixed(1)}" y="${H - 8}" text-anchor="middle" class="evo-axis-text">${r.label}</text>`;
          }
          out += `<rect class="evo-hit" x="${(padL + colW * idx).toFixed(1)}" y="${padT}" width="${colW.toFixed(1)}" height="${plotH + padB}" />`;
          out += `</g>`;
        });

        // Subtle trend line for Leads when 2+ points
        if (visible.leads && trendPoints.length > 1) {
          out += `<polyline fill="none" stroke="#1c1314" stroke-width="1.75" stroke-dasharray="4 3" opacity="0.55" points="${trendPoints.join(' ')}" pointer-events="none" />`;
        }

        svg.innerHTML = out;

        // Bind hover/tap interaction
        const cols = svg.querySelectorAll('.evo-col');
        const activate = (idx) => {
          cols.forEach((c) => c.classList.remove('is-active'));
          if (cols[idx]) cols[idx].classList.add('is-active');
          setTooltip(rows[idx]);
        };

        cols.forEach((col) => {
          const idx = Number(col.getAttribute('data-idx'));
          col.addEventListener('mouseenter', () => activate(idx));
          col.addEventListener('click', () => activate(idx));
        });

        // Highlight latest active period by default
        const defaultIdx = rows.reduce((best, r, i) => (r.visits + r.chat + r.leads > 0 ? i : best), rows.length - 1);
        if (rows[defaultIdx]) activate(defaultIdx);

        applyZoom(true);
      }

      if (zoomOutBtn) {
        zoomOutBtn.addEventListener('click', () => {
          if (zoomIdx > 0) {
            zoomIdx--;
            applyZoom(true);
          }
        });
      }

      if (zoomInBtn) {
        zoomInBtn.addEventListener('click', () => {
          if (zoomIdx < zoomSteps.length - 1) {
            zoomIdx++;
            applyZoom(true);
          }
        });
      }

      modeBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
          mode = btn.getAttribute('data-evo-mode');
          modeBtns.forEach((b) => {
            const on = b === btn;
            b.classList.toggle('active', on);
            b.setAttribute('aria-selected', on ? 'true' : 'false');
          });
          render();
        });
      });

      yearSelect.addEventListener('change', () => {
        selectedYear = yearSelect.value;
        render();
      });

      legendBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
          const s = btn.getAttribute('data-series');
          visible[s] = !visible[s];
          // Keep at least one series visible
          if (!visible.visits && !visible.chat && !visible.leads) {
            visible[s] = true;
            return;
          }
          btn.classList.toggle('is-off', !visible[s]);
          render();
        });
      });

      render();
    })();
  </script>
</body>
</html>
