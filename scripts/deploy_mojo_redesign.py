#!/usr/bin/env python3
"""
Script para generar y desplegar el rediseño bespoke de Mojo Perruquería
(https://mojoperruqueria.com) para el lead 'perruqueria-manau-barcelona'.
"""
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import sincronizar_gh_pages, LEADS_FILE, leer_leads_guardados

slug = "perruqueria-manau-barcelona"

html_content = """<!DOCTYPE html>
<html lang="ca" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>Mojo Perruquería – Peluqueria Unisex d'Autor | Poblenou Barcelona</title>
  <meta name="description" content="Mojo Perruquería a Poblenou (Barcelona). Peluqueria unisex d'autor dirigida per Àlex Sans (25+ anys d'ofici en cinema, moda i teatre). Inspirada en el blues, el rock i el cinema.">
  
  <!-- Open Graph -->
  <meta property="og:title" content="Mojo Perruquería – Peluqueria Unisex d'Autor | Poblenou Barcelona">
  <meta property="og:description" content="Inspirat en el blues americà i l'estètica cinematogràfica. 25 anys d'ofici al Poblenou. Demana la teva cita online.">
  <meta property="og:image" content="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2022/02/MOJO_WEB_7-1.jpg?fit=1920%2C900&ssl=1">
  <meta property="og:url" content="https://dga80.github.io/instaleads/perruqueria-manau-barcelona/">
  
  <!-- Fonts: Courier Prime (Original Mojo) + Plus Jakarta Sans + Space Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400;1,700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            mojo: {
              powder: '#CFECFA',
              powderLight: '#E8F6FD',
              powderDark: '#93CEEE',
              black: '#0A0B0E',
              darkCard: '#13151C',
              darkBorder: '#232734',
              red: '#FF2E2E',
              redDark: '#D41616',
              grayMuted: '#8E9AAF',
            }
          },
          fontFamily: {
            mono: ['"Courier Prime"', 'Courier', 'monospace'],
            code: ['"Space Mono"', 'monospace'],
            sans: ['"Plus Jakarta Sans"', 'sans-serif'],
          },
          animation: {
            'spin-slow': 'spin 12s linear infinite',
            'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            'marquee': 'marquee 25s linear infinite',
          },
          keyframes: {
            marquee: {
              '0%': { transform: 'translateX(0%)' },
              '100%': { transform: 'translateX(-50%)' },
            }
          }
        }
      }
    }
  </script>

  <style>
    :root {
      --sat: env(safe-area-inset-top, 0px);
      --sab: env(safe-area-inset-bottom, 0px);
    }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: #0A0B0E;
      color: #FFFFFF;
      overflow-x: hidden;
    }
    .font-typewriter {
      font-family: 'Courier Prime', Courier, monospace;
    }
    .font-spacemono {
      font-family: 'Space Mono', monospace;
    }
    .mojo-badge-border {
      box-shadow: 0 0 0 1px rgba(207, 236, 250, 0.2), 0 8px 24px -4px rgba(0, 0, 0, 0.6);
    }
    .vinyl-grooves {
      background: radial-gradient(circle, #1a1a1f 15%, #0d0e12 16%, #1a1a1f 30%, #0d0e12 31%, #1a1a1f 45%, #0d0e12 46%, #1a1a1f 60%, #0d0e12 61%, #1a1a1f 75%, #0a0b0e 100%);
    }
    @keyframes kenburns {
      0% { transform: scale(1.02) translate(0%, 0%); }
      50% { transform: scale(1.10) translate(-1.5%, -1%); }
      100% { transform: scale(1.02) translate(0%, 0%); }
    }
    @keyframes kenburnsReverse {
      0% { transform: scale(1.10) translate(0%, 0%); }
      50% { transform: scale(1.02) translate(1.5%, 1%); }
      100% { transform: scale(1.10) translate(0%, 0%); }
    }
    .animate-kenburns {
      animation: kenburns 22s ease-in-out infinite alternate;
      will-change: transform;
    }
    .animate-kenburns-reverse {
      animation: kenburnsReverse 26s ease-in-out infinite alternate;
      will-change: transform;
    }
    /* Custom scrollbar */
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: #0A0B0E;
    }
    ::-webkit-scrollbar-thumb {
      background: #232734;
      border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #CFECFA;
    }
  </style>
</head>

<body class="bg-mojo-black text-white antialiased selection:bg-mojo-powder selection:text-mojo-black">

  <!-- TOP RUNNING MARQUEE (Aesthetic Vinyl / Cinema Bar) -->
  <div class="bg-mojo-powder text-mojo-black py-1.5 overflow-hidden border-b border-mojo-black/10 font-spacemono text-[11px] font-bold uppercase tracking-wider select-none relative z-50">
    <div class="flex whitespace-nowrap animate-marquee">
      <span class="mx-4 flex items-center gap-2">✦ MOJO PERRUQUERIA POBLE NOU · BARCELONA ✦</span>
      <span class="mx-4 flex items-center gap-2">✂️ 25 ANYS D'OFICI & CINEMA</span>
      <span class="mx-4 flex items-center gap-2">🎵 MOJO SOUNDTRACK PLAYLIST ON SPOTIFY</span>
      <span class="mx-4 flex items-center gap-2">📍 CARRER DE LLULL 84, BARCELONA</span>
      <span class="mx-4 flex items-center gap-2">✦ DIMARTS A DISSABTE · CITA PRÈVIA</span>
      <span class="mx-4 flex items-center gap-2">✦ MOJO PERRUQUERIA POBLE NOU · BARCELONA ✦</span>
      <span class="mx-4 flex items-center gap-2">✂️ 25 ANYS D'OFICI & CINEMA</span>
      <span class="mx-4 flex items-center gap-2">🎵 MOJO SOUNDTRACK PLAYLIST ON SPOTIFY</span>
      <span class="mx-4 flex items-center gap-2">📍 CARRER DE LLULL 84, BARCELONA</span>
      <span class="mx-4 flex items-center gap-2">✦ DIMARTS A DISSABTE · CITA PRÈVIA</span>
    </div>
  </div>

  <!-- MAIN HEADER / NAVBAR -->
  <header class="sticky top-0 z-40 bg-mojo-black/85 backdrop-blur-md border-b border-mojo-darkBorder transition-all duration-200">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 py-3 flex items-center justify-between">
      
      <!-- Brand Logo & Identity (Sin fondo / Letras celestes puras) -->
      <a href="#inici" class="flex items-center gap-3 group">
        <img src="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2021/12/Mojo-logo-transparente.png?fit=200%2C50&ssl=1" 
             alt="Mojo Perruqueria" 
             class="h-7 sm:h-8 w-auto object-contain transition-transform group-hover:scale-105"
             style="filter: brightness(0) saturate(100%) invert(91%) sepia(13%) saturate(671%) hue-rotate(170deg) brightness(102%) contrast(98%);" />
        <div class="hidden sm:flex flex-col">
          <span class="font-typewriter text-xs font-bold tracking-widest text-mojo-powder uppercase">PERRUQUERIA D'AUTOR</span>
          <span class="text-[10px] text-mojo-grayMuted font-spacemono">POBLENOU · BCN</span>
        </div>
      </a>

      <!-- Desktop Nav Links -->
      <nav class="hidden md:flex items-center gap-6 font-spacemono text-xs font-medium">
        <a href="#concepte" class="text-neutral-300 hover:text-mojo-powder transition flex items-center gap-1.5" data-i18n="nav_concept">
          <span>01.</span> <span data-i18n="nav_concept_label">CONCEPTE</span>
        </a>
        <a href="#alex-sans" class="text-neutral-300 hover:text-mojo-powder transition flex items-center gap-1.5">
          <span>02.</span> <span>ÀLEX SANS</span>
        </a>
        <a href="#serveis" class="text-neutral-300 hover:text-mojo-powder transition flex items-center gap-1.5">
          <span>03.</span> <span data-i18n="nav_services_label">SERVEIS</span>
        </a>
        <a href="#galeria" class="text-neutral-300 hover:text-mojo-powder transition flex items-center gap-1.5">
          <span>04.</span> <span data-i18n="nav_gallery_label">GALERIA</span>
        </a>
        <a href="#horari-contacte" class="text-neutral-300 hover:text-mojo-powder transition flex items-center gap-1.5">
          <span>05.</span> <span data-i18n="nav_contact_label">CONTACTE</span>
        </a>
      </nav>

      <!-- Language Switcher & Quick CTA -->
      <div class="flex items-center gap-2.5">
        
        <!-- Interactive Language Toggle (CA / ES) -->
        <div class="flex items-center bg-mojo-darkCard p-0.5 rounded-lg border border-mojo-darkBorder text-xs font-spacemono font-bold">
          <button id="lang-btn-ca" onclick="setLanguage('ca')" class="px-2.5 py-1 rounded bg-mojo-powder text-mojo-black transition-all duration-150">
            CA
          </button>
          <button id="lang-btn-es" onclick="setLanguage('es')" class="px-2.5 py-1 rounded text-neutral-400 hover:text-white transition-all duration-150">
            ES
          </button>
        </div>

        <!-- Phone Call Quick Button -->
        <a href="tel:932440276" class="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-mojo-darkCard hover:bg-white/10 text-neutral-200 border border-mojo-darkBorder text-xs font-spacemono transition" title="Trucar al saló">
          <svg class="w-3.5 h-3.5 text-mojo-powder" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
          <span>93 244 02 76</span>
        </a>

        <!-- WhatsApp Hero CTA -->
        <a href="https://wa.me/34932440276?text=Hola%20Mojo%20Perruqueria,%20voldria%20demanar%20cita" target="_blank" class="px-3.5 sm:px-4 py-1.5 sm:py-2 rounded-lg bg-mojo-powder hover:bg-mojo-powderDark text-mojo-black font-spacemono font-bold text-xs flex items-center gap-1.5 active:scale-95 transition shadow-sm" id="header-cta-btn">
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.771-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.299.045-.677.063-1.092-.069-.252-.08-.575-.187-.988-.365-1.739-.751-2.874-2.502-2.961-2.617-.087-.116-.708-.94-.708-1.793s.448-1.273.607-1.446c.159-.173.346-.217.462-.217l.332.006c.106.005.249-.04.39.298.144.347.491 1.2.534 1.287.043.087.072.188.014.304-.058.116-.087.188-.173.289l-.26.304c-.087.086-.177.18-.076.354.101.174.449.741.964 1.201.662.591 1.221.774 1.394.86s.275.072.376-.043c.101-.116.433-.506.549-.68.116-.173.231-.145.39-.087s1.011.477 1.184.564.289.13.332.202c.045.072.045.419-.099.824z"/></svg>
          <span data-i18n="cta_header">Demanar Cita</span>
        </a>
      </div>

    </div>
  </header>

  <!-- HERO SECTION WITH CINEMATIC MOVING BACKGROUND -->
  <section id="inici" class="relative min-h-[82vh] sm:min-h-[86vh] flex items-center pt-8 pb-16 sm:pb-24 lg:pt-12 overflow-hidden">
    
    <!-- Moving Background Image with Ken Burns Effect -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none -z-20">
      <img src="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2022/02/0001-2-scaled.jpg?fit=2560%2C1200&ssl=1" 
           alt="Mojo Perruqueria Interior Panoràmica" 
           class="w-full h-full object-cover object-center animate-kenburns origin-center opacity-30 brightness-75 contrast-125 scale-105" />
    </div>

    <!-- Multi-Layer Dark Gradient Overlay for 100% Readability -->
    <div class="absolute inset-0 bg-gradient-to-r from-mojo-black via-mojo-black/95 to-mojo-black/80 -z-10"></div>
    <div class="absolute inset-0 bg-gradient-to-t from-mojo-black via-transparent to-mojo-black/85 -z-10"></div>

    <!-- Atmospheric Background Blur Glows -->
    <div class="absolute top-10 left-1/4 w-96 h-96 bg-mojo-powder/10 rounded-full blur-3xl pointer-events-none -z-10"></div>
    <div class="absolute bottom-10 right-10 w-80 h-80 bg-mojo-red/10 rounded-full blur-3xl pointer-events-none -z-10"></div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full relative z-10">
      
      <!-- Main Grid Hero -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
        
        <!-- Left Column: Copy & CTAs -->
        <div class="lg:col-span-7 space-y-6">
          <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-[1.08] text-white">
            <span class="font-typewriter text-mojo-powder block text-3xl sm:text-4xl font-normal mb-1">Mojo Perruquería</span>
            <span data-i18n="hero_title">On el teu MOJO troba la seva màxima expressió.</span>
          </h1>

          <p class="text-base sm:text-lg text-neutral-300 leading-relaxed font-sans max-w-2xl" data-i18n="hero_description">
            Inspirats en el blues americà i l'estètica cinematogràfica. Entenem cada servei com una experiència personalitzada, conduïda amb molt d'amor i sense presses, amb professionalitat i complicitat al cor del Poblenou.
          </p>

          <!-- Interactive Action Buttons -->
          <div class="flex flex-wrap items-center gap-3 pt-2">
            <a href="https://wa.me/34932440276?text=Hola%20Alex,%20voldria%20reservar%20cita%20a%20Mojo%20Perruqueria" target="_blank" class="px-6 py-3.5 rounded-xl bg-mojo-powder hover:bg-mojo-powderDark text-mojo-black font-spacemono font-bold text-sm flex items-center gap-2.5 transition active:scale-95 shadow-lg shadow-mojo-powder/10" id="hero-main-cta">
              <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.771-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.299.045-.677.063-1.092-.069-.252-.08-.575-.187-.988-.365-1.739-.751-2.874-2.502-2.961-2.617-.087-.116-.708-.94-.708-1.793s.448-1.273.607-1.446c.159-.173.346-.217.462-.217l.332.006c.106.005.249-.04.39.298.144.347.491 1.2.534 1.287.043.087.072.188.014.304-.058.116-.087.188-.173.289l-.26.304c-.087.086-.177.18-.076.354.101.174.449.741.964 1.201.662.591 1.221.774 1.394.86s.275.072.376-.043c.101-.116.433-.506.549-.68.116-.173.231-.145.39-.087s1.011.477 1.184.564.289.13.332.202c.045.072.045.419-.099.824z"/></svg>
              <span data-i18n="hero_cta_wa">Reservar per WhatsApp</span>
            </a>

            <a href="https://open.spotify.com/playlist/6GeH7YaGcQzDxPwiD7Q4DC" target="_blank" class="px-5 py-3.5 rounded-xl bg-mojo-darkCard hover:bg-white/10 text-white border border-mojo-darkBorder font-spacemono font-medium text-xs flex items-center gap-2 transition">
              <svg class="w-4 h-4 text-green-400 fill-current" viewBox="0 0 24 24"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/></svg>
              <span>Mojo Spotify Playlist</span>
            </a>
          </div>

          <!-- Quick Metrics Grid -->
          <div class="grid grid-cols-3 gap-3 sm:gap-4 pt-4 border-t border-mojo-darkBorder/60">
            <div class="bg-mojo-darkCard/70 p-3 rounded-xl border border-mojo-darkBorder">
              <div class="text-xl sm:text-2xl font-bold font-typewriter text-mojo-powder">25+</div>
              <div class="text-[11px] text-neutral-400 font-spacemono" data-i18n="stat_years">Anys d'Ofici</div>
            </div>
            <div class="bg-mojo-darkCard/70 p-3 rounded-xl border border-mojo-darkBorder">
              <div class="text-xl sm:text-2xl font-bold font-typewriter text-mojo-powder">100%</div>
              <div class="text-[11px] text-neutral-400 font-spacemono" data-i18n="stat_unisex">Unisex & Autor</div>
            </div>
            <div class="bg-mojo-darkCard/70 p-3 rounded-xl border border-mojo-darkBorder">
              <div class="text-xl sm:text-2xl font-bold font-typewriter text-mojo-powder">Poblenou</div>
              <div class="text-[11px] text-neutral-400 font-spacemono" data-i18n="stat_location">C/ Llull 84, BCN</div>
            </div>
          </div>

        </div>

        <!-- Right Column: Visual Stage with Authentic Photos & Vinyl Record -->
        <div class="lg:col-span-5 relative">
          
          <!-- Vinyl Disc Spinning Behind Photo (Visual Concept) -->
          <div class="absolute -top-6 -right-6 w-36 h-36 sm:w-48 sm:h-48 rounded-full vinyl-grooves border-4 border-neutral-800 shadow-2xl flex items-center justify-center animate-spin-slow pointer-events-none hidden sm:flex z-0 opacity-80">
            <div class="w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-mojo-red flex items-center justify-center text-white text-[9px] font-spacemono font-bold tracking-tighter text-center">
              MOJO<br>SOUND
            </div>
          </div>

          <!-- Main Hero Image Card -->
          <div class="relative z-10 rounded-2xl overflow-hidden border border-mojo-darkBorder bg-mojo-darkCard shadow-2xl group">
            <img src="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2022/02/MOJO_WEB_7-1.jpg?fit=1920%2C900&ssl=1" alt="Mojo Perruqueria Interior i Estilisme" class="w-full h-80 sm:h-96 object-cover group-hover:scale-105 transition-transform duration-500" />
            
            <div class="absolute inset-0 bg-gradient-to-t from-mojo-black via-mojo-black/20 to-transparent"></div>

            <!-- Floating Authentic Badge Top -->
            <div class="absolute top-3.5 left-3.5 bg-mojo-black/85 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 flex items-center gap-2 text-xs font-spacemono">
              <span class="w-2 h-2 rounded-full bg-mojo-powder"></span>
              <span>L'Espai de Poblenou</span>
            </div>

            <!-- Bottom Floating Quote inside Photo -->
            <div class="absolute bottom-3.5 left-3.5 right-3.5 bg-mojo-darkCard/90 backdrop-blur-md p-3 rounded-xl border border-white/10">
              <p class="font-typewriter text-xs text-mojo-powder italic">
                "Aquella essència tan preuada que només posseeixen les persones més carismàtiques."
              </p>
              <div class="mt-1 flex items-center justify-between text-[10px] text-neutral-400 font-spacemono">
                <span>— Àlex Sans (Front Man)</span>
                <span class="text-mojo-red font-bold">#MojoStyle</span>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>
  </section>

  <!-- CONCEPT SECTION: THE MOJO ESSENCE & BLUES HERITAGE -->
  <section id="concepte" class="py-16 sm:py-24 bg-[#0E1015] border-y border-mojo-darkBorder relative">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
        
        <!-- Left Column: Authentic Text from mojoperruqueria.com -->
        <div class="lg:col-span-7 space-y-5">
          <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-mojo-powder/10 text-mojo-powder font-spacemono text-xs font-semibold">
            <span>01 // CONCEPTE & FILOSOFIA</span>
          </div>

          <h2 class="text-3xl sm:text-4xl font-extrabold text-white font-sans tracking-tight" data-i18n="concept_heading">
            Què és el <span class="font-typewriter text-mojo-powder">MOJO</span>?
          </h2>

          <div class="space-y-4 text-neutral-300 font-sans leading-relaxed text-sm sm:text-base">
            <p data-i18n="concept_p1">
              El concepte de <strong>MOJO</strong>, inspirat en el blues americà, és la qualitat o habilitat d'atraure la gent cap a tu, aquella essència tan preuada que només posseeixen les persones més carismàtiques.
            </p>
            <p data-i18n="concept_p2">
              Al nostre espai comptem amb un equip format pels millors professionals que trauran el màxim partit de totes les teves qualitats. Ens agrada pensar els nostres serveis com una experiència personalitzada, conduïda amb molt d'amor i poca pressa, amb professionalitat i complicitat.
            </p>
            <p data-i18n="concept_p3">
              Vine a veure'ns i gaudeix del nostre acollidor espai al fantàstic barri de Poblenou, on podràs compartir amb nosaltres passions com la música o el cinema, d'on procedeixen la gran majoria de les nostres influències.
            </p>
          </div>

          <!-- Feature Bullets -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <div class="flex items-center gap-3 p-3 rounded-xl bg-mojo-darkCard border border-mojo-darkBorder">
              <span class="text-xl">🎸</span>
              <div>
                <div class="text-xs font-bold text-white font-spacemono" data-i18n="feat_1_title">Influència Musical & Blues</div>
                <div class="text-[11px] text-neutral-400" data-i18n="feat_1_desc">Ambient càlid amb banda sonora cuidada</div>
              </div>
            </div>
            <div class="flex items-center gap-3 p-3 rounded-xl bg-mojo-darkCard border border-mojo-darkBorder">
              <span class="text-xl">☕️</span>
              <div>
                <div class="text-xs font-bold text-white font-spacemono" data-i18n="feat_2_title">Sense Presses, Amb Amor</div>
                <div class="text-[11px] text-neutral-400" data-i18n="feat_2_desc">Dedicació exclusiva per a cada client</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Interactive Vinyl Player Widget -->
        <div class="lg:col-span-5">
          <div class="bg-mojo-darkCard p-6 rounded-2xl border border-mojo-darkBorder shadow-2xl relative overflow-hidden space-y-4">
            
            <div class="flex items-center justify-between border-b border-mojo-darkBorder pb-3">
              <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse"></span>
                <span class="text-xs font-spacemono text-neutral-300">MOJO SOUNDTRACK STREAM</span>
              </div>
              <span class="text-[10px] font-spacemono bg-mojo-powder/15 text-mojo-powder px-2 py-0.5 rounded">SPOTIFY OFFICIAL</span>
            </div>

            <!-- Vinyl Animation Card -->
            <div class="flex items-center gap-4 bg-mojo-black p-4 rounded-xl border border-white/5">
              <div class="w-16 h-16 rounded-full vinyl-grooves border-2 border-neutral-700 flex items-center justify-center shrink-0 animate-spin-slow">
                <div class="w-6 h-6 rounded-full bg-mojo-red flex items-center justify-center text-[7px] font-bold text-white font-spacemono">
                  MOJO
                </div>
              </div>
              <div class="min-w-0 flex-1">
                <div class="text-xs font-bold text-white truncate font-spacemono">Mojo Perruqueria Playlist</div>
                <div class="text-[11px] text-mojo-powder truncate font-sans">Blues, Rock, Soul & Cinema Tracks</div>
                <div class="text-[10px] text-neutral-500 font-spacemono mt-0.5">Selecció oficial d'Àlex Sans</div>
              </div>
            </div>

            <!-- Direct Spotify Link Button -->
            <a href="https://open.spotify.com/playlist/6GeH7YaGcQzDxPwiD7Q4DC" target="_blank" class="w-full py-2.5 px-4 rounded-xl bg-green-600 hover:bg-green-500 text-white font-spacemono text-xs font-bold flex items-center justify-center gap-2 transition active:scale-95 shadow-md">
              <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/></svg>
              <span data-i18n="spotify_cta">Obrir Playlist a Spotify</span>
            </a>

            <!-- Supporting Salon Photo -->
            <div class="rounded-xl overflow-hidden border border-white/10">
              <img src="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2022/02/MOJO_WEB_3-1.jpg?fit=1920%2C900&ssl=1" alt="Mojo Perruqueria Salon Poblenou" class="w-full h-36 object-cover" />
            </div>

          </div>
        </div>

      </div>

    </div>
  </section>

  <!-- FRONT MAN SPOTLIGHT: ÀLEX SANS -->
  <section id="alex-sans" class="py-16 sm:py-24 bg-mojo-black relative overflow-hidden">
    
    <!-- Moving Ambient Background -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none -z-20">
      <img src="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2022/02/MOJO_WEB_6-1.jpg?fit=1920%2C900&ssl=1" 
           alt="Mojo Perruqueria Ambient" 
           class="w-full h-full object-cover animate-kenburns-reverse opacity-20 brightness-50" />
    </div>
    <div class="absolute inset-0 bg-gradient-to-b from-mojo-black via-mojo-black/90 to-mojo-black -z-10"></div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
      
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
        
        <!-- Left Column: Photo Frame -->
        <div class="lg:col-span-5 order-2 lg:order-1">
          <div class="relative rounded-2xl overflow-hidden border border-mojo-darkBorder bg-mojo-darkCard shadow-2xl">
            <img src="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2022/02/MOJO_WEB_2-1.jpg?fit=1920%2C900&ssl=1" alt="Àlex Sans tallant els cabells a Mojo Perruqueria" class="w-full h-80 sm:h-96 object-cover" />
            <div class="absolute inset-0 bg-gradient-to-t from-mojo-black via-transparent to-transparent"></div>
            
            <div class="absolute bottom-4 left-4 right-4 bg-mojo-black/90 backdrop-blur-md p-3.5 rounded-xl border border-white/10">
              <div class="text-xs font-spacemono font-bold text-mojo-powder">Àlex Sans</div>
              <div class="text-[11px] text-neutral-400 font-sans" data-i18n="alex_role">Fundador & Front Man de Mojo Perruquería</div>
            </div>
          </div>
        </div>

        <!-- Right Column: Biography & Trajectory -->
        <div class="lg:col-span-7 order-1 lg:order-2 space-y-6">
          <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-mojo-red/10 text-mojo-red font-spacemono text-xs font-semibold">
            <span>02 // EL FRONT MAN</span>
          </div>

          <h2 class="text-3xl sm:text-4xl font-extrabold text-white font-sans tracking-tight">
            Àlex Sans <span class="text-mojo-powder font-typewriter text-2xl sm:text-3xl font-normal block sm:inline">· 25+ Anys d'Ofici</span>
          </h2>

          <div class="space-y-4 text-neutral-300 font-sans leading-relaxed text-sm sm:text-base">
            <p data-i18n="alex_p1">
              El nostre <em>front man</em>, <strong>Àlex Sans</strong>, compta amb una carrera de més de 25 anys vinculada al món de l'estètica.
            </p>
            <p data-i18n="alex_p2">
              Ha treballat tant en reconeguts salons de perruqueria com dintre del món de l'audiovisual, exercint com a perruquer i estilista en <strong>cinema, teatre, publicitat, televisió i passarel·les de moda</strong>.
            </p>
            <p class="font-typewriter text-mojo-powder bg-mojo-darkCard p-4 rounded-xl border border-mojo-darkBorder" data-i18n="alex_quote">
              "Ara ha arribat el moment de compartir el seu propi projecte, una perruqueria d'autor on el vostre MOJO estarà en les millors mans."
            </p>
          </div>

          <!-- Editorial Trajectory Pills -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-2 text-center font-spacemono text-xs">
            <div class="p-2.5 rounded-lg bg-mojo-darkCard border border-mojo-darkBorder text-neutral-200">
              <span class="block text-base">🎬</span> Cinema
            </div>
            <div class="p-2.5 rounded-lg bg-mojo-darkCard border border-mojo-darkBorder text-neutral-200">
              <span class="block text-base">🎭</span> Teatre
            </div>
            <div class="p-2.5 rounded-lg bg-mojo-darkCard border border-mojo-darkBorder text-neutral-200">
              <span class="block text-base">📺</span> Televisió
            </div>
            <div class="p-2.5 rounded-lg bg-mojo-darkCard border border-mojo-darkBorder text-neutral-200">
              <span class="block text-base">👠</span> Moda & Pasarela
            </div>
          </div>

        </div>

      </div>

    </div>
  </section>

  <!-- INTERACTIVE SERVICES & PRICING MENU -->
  <section id="serveis" class="py-16 sm:py-24 bg-[#0E1015] border-t border-mojo-darkBorder relative">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <!-- Section Header -->
      <div class="text-center max-w-3xl mx-auto mb-12 space-y-3">
        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-mojo-powder/10 text-mojo-powder font-spacemono text-xs font-semibold">
          <span>03 // CARTA DE SERVEIS D'AUTOR</span>
        </div>
        <h2 class="text-3xl sm:text-4xl font-extrabold text-white font-sans tracking-tight" data-i18n="services_heading">
          Talls, Color & Cures Personalitzades
        </h2>
        <p class="text-sm sm:text-base text-neutral-400 font-sans" data-i18n="services_subheading">
          Tècniques precises adaptades a la textura del teu cabell i a la teva personalitat. Selecciona un servei per demanar cita directa.
        </p>
      </div>

      <!-- Service Categories Tabs -->
      <div class="flex flex-wrap items-center justify-center gap-2 mb-8 font-spacemono text-xs">
        <button onclick="filterServices('all')" id="tab-all" class="px-4 py-2 rounded-lg bg-mojo-powder text-mojo-black font-bold transition">
          Tots els Serveis
        </button>
        <button onclick="filterServices('tall')" id="tab-tall" class="px-4 py-2 rounded-lg bg-mojo-darkCard text-neutral-300 hover:text-white border border-mojo-darkBorder transition">
          ✂️ Talls & Estilisme
        </button>
        <button onclick="filterServices('color')" id="tab-color" class="px-4 py-2 rounded-lg bg-mojo-darkCard text-neutral-300 hover:text-white border border-mojo-darkBorder transition">
          🎨 Colorimetria & Metxes
        </button>
        <button onclick="filterServices('ritual')" id="tab-ritual" class="px-4 py-2 rounded-lg bg-mojo-darkCard text-neutral-300 hover:text-white border border-mojo-darkBorder transition">
          🌿 Tractaments & Barberia
        </button>
      </div>

      <!-- Services Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="services-grid">
        
        <!-- Service 1: Tall Unisex d'Autor -->
        <div class="service-item bg-mojo-darkCard p-6 rounded-2xl border border-mojo-darkBorder hover:border-mojo-powder/40 transition-all duration-200 flex flex-col justify-between" data-category="tall">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-spacemono text-mojo-powder font-bold">#TALL-01</span>
              <span class="text-xs font-spacemono text-neutral-400">45-60 min</span>
            </div>
            <h3 class="text-lg font-bold text-white font-sans" data-i18n="srv_1_name">Tall Unisex d'Autor</h3>
            <p class="text-xs text-neutral-400 font-sans leading-relaxed" data-i18n="srv_1_desc">
              Assessorament morfològic personalitzat, rentat amb xampú de tractament, tall a mà alçada o navalla i assecat/estilisme natural.
            </p>
          </div>
          <div class="pt-5 mt-4 border-t border-mojo-darkBorder flex items-center justify-between">
            <span class="text-xs text-neutral-400 font-spacemono">Consultar segons llargada</span>
            <a href="https://wa.me/34932440276?text=Hola%20Mojo,%20voldria%20demanar%20cita%20per%20un%20Tall%20Unisex%20d'Autor" target="_blank" class="px-3 py-1.5 rounded-lg bg-mojo-powder hover:bg-mojo-powderDark text-mojo-black font-spacemono font-bold text-xs transition">
              Reservar
            </a>
          </div>
        </div>

        <!-- Service 2: Colorimetria & Balayage Creatiu -->
        <div class="service-item bg-mojo-darkCard p-6 rounded-2xl border border-mojo-darkBorder hover:border-mojo-powder/40 transition-all duration-200 flex flex-col justify-between" data-category="color">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-spacemono text-mojo-powder font-bold">#COLOR-02</span>
              <span class="text-xs font-spacemono text-neutral-400">90-120 min</span>
            </div>
            <h3 class="text-lg font-bold text-white font-sans" data-i18n="srv_2_name">Colorimetria & Balayage Creatiu</h3>
            <p class="text-xs text-neutral-400 font-sans leading-relaxed" data-i18n="srv_2_desc">
              Tècniques de metxes, degradats suaus, babylights o cobertura total amb productes respectuosos amb la fibra capil·lar.
            </p>
          </div>
          <div class="pt-5 mt-4 border-t border-mojo-darkBorder flex items-center justify-between">
            <span class="text-xs text-neutral-400 font-spacemono">Diagnòstic previ</span>
            <a href="https://wa.me/34932440276?text=Hola%20Mojo,%20voldria%20demanar%20cita%20per%20Color%20o%20Balayage" target="_blank" class="px-3 py-1.5 rounded-lg bg-mojo-powder hover:bg-mojo-powderDark text-mojo-black font-spacemono font-bold text-xs transition">
              Reservar
            </a>
          </div>
        </div>

        <!-- Service 3: Tractament Hidratant & Reconstructor -->
        <div class="service-item bg-mojo-darkCard p-6 rounded-2xl border border-mojo-darkBorder hover:border-mojo-powder/40 transition-all duration-200 flex flex-col justify-between" data-category="ritual">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-spacemono text-mojo-powder font-bold">#CARE-03</span>
              <span class="text-xs font-spacemono text-neutral-400">30-45 min</span>
            </div>
            <h3 class="text-lg font-bold text-white font-sans" data-i18n="srv_3_name">Ritual de Reconstrucció Capil·lar</h3>
            <p class="text-xs text-neutral-400 font-sans leading-relaxed" data-i18n="srv_3_desc">
              Tractament intensiu d'àcid hialurònic i proteïnes orgàniques per retornar brillantor, elasticitat i força al cabell danyat.
            </p>
          </div>
          <div class="pt-5 mt-4 border-t border-mojo-darkBorder flex items-center justify-between">
            <span class="text-xs text-neutral-400 font-spacemono">Brillantor & Nutrició</span>
            <a href="https://wa.me/34932440276?text=Hola%20Mojo,%20voldria%20demanar%20cita%20per%20un%20Tractament%20Capil%C2%B7lar" target="_blank" class="px-3 py-1.5 rounded-lg bg-mojo-powder hover:bg-mojo-powderDark text-mojo-black font-spacemono font-bold text-xs transition">
              Reservar
            </a>
          </div>
        </div>

        <!-- Service 4: Pentinat Editorial & Esdeveniments -->
        <div class="service-item bg-mojo-darkCard p-6 rounded-2xl border border-mojo-darkBorder hover:border-mojo-powder/40 transition-all duration-200 flex flex-col justify-between" data-category="tall">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-spacemono text-mojo-powder font-bold">#STYLE-04</span>
              <span class="text-xs font-spacemono text-neutral-400">40 min</span>
            </div>
            <h3 class="text-lg font-bold text-white font-sans" data-i18n="srv_4_name">Pentinat Editorial & Esdeveniments</h3>
            <p class="text-xs text-neutral-400 font-sans leading-relaxed" data-i18n="srv_4_desc">
              Estilisme professional per a rodatges, sessions de fotos, bodes o cites especials amb segell d'autor cinematogràfic.
            </p>
          </div>
          <div class="pt-5 mt-4 border-t border-mojo-darkBorder flex items-center justify-between">
            <span class="text-xs text-neutral-400 font-spacemono">Acabat professional</span>
            <a href="https://wa.me/34932440276?text=Hola%20Mojo,%20voldria%20demanar%20cita%20per%20Pentinat%20Editorial" target="_blank" class="px-3 py-1.5 rounded-lg bg-mojo-powder hover:bg-mojo-powderDark text-mojo-black font-spacemono font-bold text-xs transition">
              Reservar
            </a>
          </div>
        </div>

        <!-- Service 5: Matís, Gloss & To sobre To -->
        <div class="service-item bg-mojo-darkCard p-6 rounded-2xl border border-mojo-darkBorder hover:border-mojo-powder/40 transition-all duration-200 flex flex-col justify-between" data-category="color">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-spacemono text-mojo-powder font-bold">#GLOSS-05</span>
              <span class="text-xs font-spacemono text-neutral-400">45 min</span>
            </div>
            <h3 class="text-lg font-bold text-white font-sans" data-i18n="srv_5_name">Bany de Color & Gloss Brillantor</h3>
            <p class="text-xs text-neutral-400 font-sans leading-relaxed" data-i18n="srv_5_desc">
              Reviure el to, neutralitzar reflexes no desitjats i aportar un bany de llum intens sense alterar la base natural.
            </p>
          </div>
          <div class="pt-5 mt-4 border-t border-mojo-darkBorder flex items-center justify-between">
            <span class="text-xs text-neutral-400 font-spacemono">Extra Brillantor</span>
            <a href="https://wa.me/34932440276?text=Hola%20Mojo,%20voldria%20demanar%20cita%20per%20un%20Bany%20de%20Color%20o%20Gloss" target="_blank" class="px-3 py-1.5 rounded-lg bg-mojo-powder hover:bg-mojo-powderDark text-mojo-black font-spacemono font-bold text-xs transition">
              Reservar
            </a>
          </div>
        </div>

        <!-- Service 6: Barberia Clàssica & Cura de Barba -->
        <div class="service-item bg-mojo-darkCard p-6 rounded-2xl border border-mojo-darkBorder hover:border-mojo-powder/40 transition-all duration-200 flex flex-col justify-between" data-category="ritual">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-xs font-spacemono text-mojo-powder font-bold">#BARBER-06</span>
              <span class="text-xs font-spacemono text-neutral-400">30 min</span>
            </div>
            <h3 class="text-lg font-bold text-white font-sans" data-i18n="srv_6_name">Afaitat Clàssic & Arreglo de Barba</h3>
            <p class="text-xs text-neutral-400 font-sans leading-relaxed" data-i18n="srv_6_desc">
              Ritual amb tovallola calenta, perfilat amb navalla tradicional, hidratació amb olis essencials i massatge facial.
            </p>
          </div>
          <div class="pt-5 mt-4 border-t border-mojo-darkBorder flex items-center justify-between">
            <span class="text-xs text-neutral-400 font-spacemono">Ritual Tradicional</span>
            <a href="https://wa.me/34932440276?text=Hola%20Mojo,%20voldria%20demanar%20cita%20per%20Arreglo%20de%20Barba" target="_blank" class="px-3 py-1.5 rounded-lg bg-mojo-powder hover:bg-mojo-powderDark text-mojo-black font-spacemono font-bold text-xs transition">
              Reservar
            </a>
          </div>
        </div>

      </div>

    </div>
  </section>

  <!-- AUTHENTIC GALLERY SHOWCASE -->
  <section id="galeria" class="py-16 sm:py-24 bg-mojo-black relative">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <!-- Section Header -->
      <div class="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-4">
        <div>
          <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-mojo-powder/10 text-mojo-powder font-spacemono text-xs font-semibold mb-2">
            <span>04 // GALERIA VISUAL</span>
          </div>
          <h2 class="text-3xl sm:text-4xl font-extrabold text-white font-sans tracking-tight" data-i18n="gallery_heading">
            L'Espai & Els Treballs a Poblenou
          </h2>
        </div>
        <a href="https://www.instagram.com/mojoperruqueria/" target="_blank" class="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-mojo-darkCard hover:bg-white/10 text-mojo-powder border border-mojo-darkBorder font-spacemono text-xs font-bold transition">
          <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
          <span>@mojoperruqueria a Instagram</span>
        </a>
      </div>

      <!-- Photo Masonry Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
        
        <div class="group relative rounded-2xl overflow-hidden border border-mojo-darkBorder bg-mojo-darkCard h-72">
          <img src="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2022/02/MOJO_WEB_6-1.jpg?fit=1920%2C900&ssl=1" alt="Mojo Perruqueria Interior" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
            <span class="text-xs font-spacemono text-mojo-powder">✦ Racó Vintage & Miralls</span>
          </div>
        </div>

        <div class="group relative rounded-2xl overflow-hidden border border-mojo-darkBorder bg-mojo-darkCard h-72">
          <img src="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2022/02/MOJO_WEB_5-1.jpg?fit=1920%2C900&ssl=1" alt="Mojo Perruqueria Barberia" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
            <span class="text-xs font-spacemono text-mojo-powder">✦ Zona de Rentat & Relax</span>
          </div>
        </div>

        <div class="group relative rounded-2xl overflow-hidden border border-mojo-darkBorder bg-mojo-darkCard h-72">
          <img src="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2022/02/MOJO_WEB_1-1.jpg?fit=1920%2C900&ssl=1" alt="Mojo Perruqueria Detalls" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
            <span class="text-xs font-spacemono text-mojo-powder">✦ Eines & Productes Professionals</span>
          </div>
        </div>

        <div class="group relative rounded-2xl overflow-hidden border border-mojo-darkBorder bg-mojo-darkCard h-72">
          <img src="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2022/02/MOJO_WEB_4-1.jpg?fit=1920%2C900&ssl=1" alt="Mojo Perruqueria Poblenou" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
            <span class="text-xs font-spacemono text-mojo-powder">✦ Estètica Industrial & Llums Càlides</span>
          </div>
        </div>

        <div class="group relative rounded-2xl overflow-hidden border border-mojo-darkBorder bg-mojo-darkCard h-72 sm:col-span-2 lg:col-span-2">
          <img src="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2022/02/0001-2-scaled.jpg?fit=2560%2C1200&ssl=1" alt="Mojo Perruqueria Panoràmica" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex items-end p-4 sm:p-6">
            <div>
              <span class="text-xs font-spacemono text-mojo-powder block mb-1">✦ MOJO PERRUQUERIA · CARRER DE LLULL 84</span>
              <span class="text-sm font-bold text-white font-sans">Un espai pensat per sentir-te a gust des del primer minut.</span>
            </div>
          </div>
        </div>

      </div>

    </div>
  </section>

  <!-- SCHEDULE, CONTACT & LOCATION SECTION -->
  <section id="horari-contacte" class="py-16 sm:py-24 bg-[#0E1015] border-t border-mojo-darkBorder relative">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-10">
        
        <!-- Left: Horaris & Contact Information -->
        <div class="lg:col-span-6 space-y-6">
          <div>
            <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-mojo-powder/10 text-mojo-powder font-spacemono text-xs font-semibold mb-2">
              <span>05 // HORARIS & LOCALITZACIÓ</span>
            </div>
            <h2 class="text-3xl sm:text-4xl font-extrabold text-white font-sans tracking-tight" data-i18n="contact_heading">
              Vine a Veure'ns a Poblenou
            </h2>
          </div>

          <!-- Real-Time Open Status Dynamic Badge -->
          <div id="realtime-status-badge" class="p-3.5 rounded-xl bg-mojo-darkCard border border-mojo-darkBorder flex items-center justify-between font-spacemono text-xs">
            <div class="flex items-center gap-2.5">
              <span id="status-indicator-dot" class="w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse"></span>
              <span id="status-text" class="text-white font-bold">Obert Avui</span>
            </div>
            <span class="text-neutral-400 text-[11px]" id="status-time-hint">10:00h - 20:00h</span>
          </div>

          <!-- Schedule Grid -->
          <div class="bg-mojo-darkCard p-6 rounded-2xl border border-mojo-darkBorder space-y-3 font-spacemono text-xs">
            <div class="text-sm font-bold text-mojo-powder font-typewriter border-b border-mojo-darkBorder pb-2">
              HORARI DE CITA PRÈVIA
            </div>
            
            <div class="flex justify-between py-1.5 border-b border-white/5">
              <span class="text-neutral-300" data-i18n="day_tue_fri">Dimarts a Divendres</span>
              <span class="text-white font-bold">10:00 – 20:00h</span>
            </div>

            <div class="flex justify-between py-1.5 border-b border-white/5">
              <span class="text-neutral-300" data-i18n="day_sat">Dissabte</span>
              <span class="text-white font-bold">10:00 – 14:00h</span>
            </div>

            <div class="flex justify-between py-1.5 text-neutral-500">
              <span data-i18n="day_sun_mon">Diumenge & Dilluns</span>
              <span class="italic" data-i18n="closed_label">Tancat per descans</span>
            </div>
          </div>

          <!-- Contact Cards Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            
            <!-- Address Card -->
            <a href="https://maps.google.com/?q=Carrer+de+Llull+84+08005+Barcelona" target="_blank" class="p-4 rounded-xl bg-mojo-darkCard hover:bg-white/5 border border-mojo-darkBorder transition group">
              <div class="text-mojo-powder text-lg mb-1">📍</div>
              <div class="text-xs font-bold text-white font-spacemono">Adreça</div>
              <div class="text-[11px] text-neutral-300 mt-0.5">Carrer de Llull, 84</div>
              <div class="text-[10px] text-neutral-400">08005 Poblenou, Barcelona</div>
              <div class="text-[10px] text-mojo-powder mt-2 group-hover:underline font-spacemono">↗ Obrir a Google Maps</div>
            </a>

            <!-- Phone Card -->
            <a href="tel:932440276" class="p-4 rounded-xl bg-mojo-darkCard hover:bg-white/5 border border-mojo-darkBorder transition group">
              <div class="text-mojo-powder text-lg mb-1">📞</div>
              <div class="text-xs font-bold text-white font-spacemono">Telèfon</div>
              <div class="text-sm font-bold text-white mt-0.5">93 244 02 76</div>
              <div class="text-[10px] text-neutral-400">Trucada directa al saló</div>
              <div class="text-[10px] text-mojo-powder mt-2 group-hover:underline font-spacemono">↗ Trucar ara</div>
            </a>

            <!-- WhatsApp Direct Card -->
            <a href="https://wa.me/34932440276?text=Hola%20Mojo%20Perruqueria,%20voldria%20demanar%20cita" target="_blank" class="p-4 rounded-xl bg-mojo-darkCard hover:bg-white/5 border border-mojo-darkBorder transition group">
              <div class="text-green-400 text-lg mb-1">💬</div>
              <div class="text-xs font-bold text-white font-spacemono">WhatsApp</div>
              <div class="text-sm font-bold text-white mt-0.5">Cita Ràpida Online</div>
              <div class="text-[10px] text-neutral-400">Resposta directa</div>
              <div class="text-[10px] text-green-400 mt-2 group-hover:underline font-spacemono">↗ Enviar missatge</div>
            </a>

            <!-- Email Card -->
            <a href="mailto:info@mojoperruqueria.com" class="p-4 rounded-xl bg-mojo-darkCard hover:bg-white/5 border border-mojo-darkBorder transition group">
              <div class="text-mojo-powder text-lg mb-1">✉️</div>
              <div class="text-xs font-bold text-white font-spacemono">Correu Electrònic</div>
              <div class="text-xs font-semibold text-white mt-0.5 truncate">info@mojoperruqueria.com</div>
              <div class="text-[10px] text-neutral-400">Per a consultes i cinema</div>
              <div class="text-[10px] text-mojo-powder mt-2 group-hover:underline font-spacemono">↗ Escriure email</div>
            </a>

          </div>

        </div>

        <!-- Right: Map Embed & Transit info -->
        <div class="lg:col-span-6 space-y-4">
          
          <div class="bg-mojo-darkCard p-2 rounded-2xl border border-mojo-darkBorder overflow-hidden shadow-2xl h-[340px] sm:h-[400px]">
            <iframe 
              src="https://maps.google.com/maps?q=Carrer+de+Llull+84+08005+Barcelona&t=&z=16&ie=UTF8&iwloc=&output=embed" 
              class="w-full h-full rounded-xl border-0" 
              allowfullscreen="" 
              loading="lazy" 
              referrerpolicy="no-referrer-when-downgrade"
              style="filter: invert(90%) hue-rotate(180deg) contrast(110%);">
            </iframe>
          </div>

          <!-- Public Transit Guide -->
          <div class="p-4 rounded-xl bg-mojo-darkCard border border-mojo-darkBorder flex items-center justify-between font-spacemono text-xs">
            <div class="flex items-center gap-3">
              <span class="text-lg">🚇</span>
              <div>
                <span class="text-white font-bold">Com arribar en transport públic:</span>
                <span class="text-neutral-400 block text-[11px]">Metro L4 (Llacuna / Bogatell) · Bus H14, 6, V25</span>
              </div>
            </div>
            <a href="https://maps.google.com/?q=Carrer+de+Llull+84+08005+Barcelona" target="_blank" class="px-3 py-1 rounded bg-white/10 hover:bg-white/20 text-white transition shrink-0">
              Ruta
            </a>
          </div>

        </div>

      </div>

    </div>
  </section>

  <!-- FOOTER -->
  <footer class="bg-mojo-black border-t border-mojo-darkBorder py-12 pb-24 sm:pb-12 text-xs font-spacemono">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
      
      <div class="flex flex-col sm:flex-row items-center justify-between gap-6">
        
        <!-- Logo & Tagline (Sin fondo) -->
        <div class="flex items-center gap-3">
          <img src="https://i0.wp.com/mojoperruqueria.com/wp-content/uploads/2021/12/Mojo-logo-transparente.png?fit=200%2C50&ssl=1" 
               alt="Mojo Perruqueria" 
               class="h-6 w-auto object-contain"
               style="filter: brightness(0) saturate(100%) invert(91%) sepia(13%) saturate(671%) hue-rotate(170deg) brightness(102%) contrast(98%);" />
          <span class="text-neutral-400 text-[11px]">Poblenou · Barcelona · 25+ Anys d'Ofici</span>
        </div>

        <!-- Social Icons -->
        <div class="flex items-center gap-4">
          <a href="https://www.instagram.com/mojoperruqueria/" target="_blank" class="p-2 rounded-lg bg-mojo-darkCard hover:bg-white/10 text-neutral-300 hover:text-white transition" title="Instagram">
            <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
          </a>
          <a href="https://open.spotify.com/playlist/6GeH7YaGcQzDxPwiD7Q4DC" target="_blank" class="p-2 rounded-lg bg-mojo-darkCard hover:bg-white/10 text-neutral-300 hover:text-white transition" title="Spotify">
            <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/></svg>
          </a>
          <a href="https://www.facebook.com/MojoPerruqueria" target="_blank" class="p-2 rounded-lg bg-mojo-darkCard hover:bg-white/10 text-neutral-300 hover:text-white transition" title="Facebook">
            <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
          </a>
        </div>

      </div>

      <div class="pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between text-neutral-500 text-[10px] gap-2">
        <div>
          © 2026 Mojo Perruquería · Llull 84, Poblenou (Barcelona). Tots els drets reservats.
        </div>
        <div>
          Proposta de redisseny UX/UI Mobile-First per Daniel García.
        </div>
      </div>

    </div>
  </footer>

  <!-- STICKY MOBILE BOTTOM BAR (High Conversion WhatsApp & Call) -->
  <div class="fixed bottom-0 left-0 right-0 z-50 bg-mojo-black/95 backdrop-blur-lg border-t border-mojo-darkBorder p-2.5 px-4 md:hidden flex items-center justify-between gap-3 shadow-2xl" style="padding-bottom: max(10px, var(--sab));">
    
    <!-- Phone Call Button -->
    <a href="tel:932440276" class="flex-1 py-2.5 rounded-xl bg-mojo-darkCard hover:bg-white/10 text-white border border-mojo-darkBorder font-spacemono font-bold text-xs flex items-center justify-center gap-1.5 transition">
      <svg class="w-3.5 h-3.5 text-mojo-powder" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
      <span>Trucar</span>
    </a>

    <!-- WhatsApp Main Button -->
    <a href="https://wa.me/34932440276?text=Hola%20Mojo%20Perruqueria,%20voldria%20demanar%20cita" target="_blank" class="flex-[1.5] py-2.5 rounded-xl bg-mojo-powder text-mojo-black font-spacemono font-bold text-xs flex items-center justify-center gap-1.5 shadow-md active:scale-95 transition" id="mobile-sticky-cta">
      <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.771-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.299.045-.677.063-1.092-.069-.252-.08-.575-.187-.988-.365-1.739-.751-2.874-2.502-2.961-2.617-.087-.116-.708-.94-.708-1.793s.448-1.273.607-1.446c.159-.173.346-.217.462-.217l.332.006c.106.005.249-.04.39.298.144.347.491 1.2.534 1.287.043.087.072.188.014.304-.058.116-.087.188-.173.289l-.26.304c-.087.086-.177.18-.076.354.101.174.449.741.964 1.201.662.591 1.221.774 1.394.86s.275.072.376-.043c.101-.116.433-.506.549-.68.116-.173.231-.145.39-.087s1.011.477 1.184.564.289.13.332.202c.045.072.045.419-.099.824z"/></svg>
      <span data-i18n="cta_sticky_mobile">Demanar Cita</span>
    </a>

  </div>

  <!-- JAVASCRIPT: BILINGUAL TRANSLATION & REALTIME OPENING HOURS -->
  <script>
    const translations = {
      ca: {
        nav_concept_label: "CONCEPTE",
        nav_services_label: "SERVEIS",
        nav_gallery_label: "GALERIA",
        nav_contact_label: "CONTACTE",
        cta_header: "Demanar Cita",
        hero_title: "On el teu MOJO troba la seva màxima expressió.",
        hero_description: "Inspirats en el blues americà i l'estètica cinematogràfica. Entenem cada servei com una experiència personalitzada, conduïda amb molt d'amor i sense presses, amb professionalitat i complicitat al cor del Poblenou.",
        hero_cta_wa: "Reservar per WhatsApp",
        stat_years: "Anys d'Ofici",
        stat_unisex: "Unisex & Autor",
        stat_location: "C/ Llull 84, BCN",
        concept_heading: "Què és el <span class='font-typewriter text-mojo-powder'>MOJO</span>?",
        concept_p1: "El concepte de <strong>MOJO</strong>, inspirat en el blues americà, és la qualitat o habilitat d'atraure la gent cap a tu, aquella essència tan preuada que només posseeixen les persones més carismàtiques.",
        concept_p2: "Al nostre espai comptem amb un equip format pels millors professionals que trauran el màxim partit de totes les teves qualitats. Ens agrada pensar els nostres serveis com una experiència personalitzada, conduïda amb molt d'amor i poca pressa, amb professionalitat i complicitat.",
        concept_p3: "Vine a veure'ns i gaudeix del nostre acollidor espai al fantàstic barri de Poblenou, on podràs compartir amb nosaltres passions com la música o el cinema, d'on procedeixen la gran majoria de les nostres influències.",
        feat_1_title: "Influència Musical & Blues",
        feat_1_desc: "Ambient càlid amb banda sonora cuidada",
        feat_2_title: "Sense Presses, Amb Amor",
        feat_2_desc: "Dedicació exclusiva per a cada client",
        spotify_cta: "Obrir Playlist a Spotify",
        alex_role: "Fundador & Front Man de Mojo Perruquería",
        alex_p1: "El nostre <em>front man</em>, <strong>Àlex Sans</strong>, compta amb una carrera de més de 25 anys vinculada al món de l'estètica.",
        alex_p2: "Ha treballat tant en reconeguts salons de perruqueria com dintre del món de l'audiovisual, exercint com a perruquer i estilista en <strong>cinema, teatre, publicitat, televisió i passarel·les de moda</strong>.",
        alex_quote: '"Ara ha arribat el moment de compartir el seu propi projecte, una perruqueria d\'autor on el vostre MOJO estarà en les millors mans."',
        services_heading: "Talls, Color & Cures Personalitzades",
        services_subheading: "Tècniques precises adaptades a la textura del teu cabell i a la teva personalitat. Selecciona un servei per demanar cita directa.",
        srv_1_name: "Tall Unisex d'Autor",
        srv_1_desc: "Assessorament morfològic personalitzat, rentat amb xampú de tractament, tall a mà alçada o navalla i assecat/estilisme natural.",
        srv_2_name: "Colorimetria & Balayage Creatiu",
        srv_2_desc: "Tècniques de metxes, degradats suaus, babylights o cobertura total amb productes respectuosos amb la fibra capil·lar.",
        srv_3_name: "Ritual de Reconstrucció Capil·lar",
        srv_3_desc: "Tractament intensiu d'àcid hialurònic i proteïnes orgàniques per retornar brillantor, elasticitat i força al cabell danyat.",
        srv_4_name: "Pentinat Editorial & Esdeveniments",
        srv_4_desc: "Estilisme professional per a rodatges, sessions de fotos, bodes o cites especials amb segell d'autor cinematogràfic.",
        srv_5_name: "Bany de Color & Gloss Brillantor",
        srv_5_desc: "Reviure el to, neutralitzar reflexes no desitjats i aportar un bany de llum intens sense alterar la base natural.",
        srv_6_name: "Afaitat Clàssic & Arreglo de Barba",
        srv_6_desc: "Ritual amb tovallola calenta, perfilat amb navalla tradicional, hidratació amb olis essencials i massatge facial.",
        gallery_heading: "L'Espai & Els Treballs a Poblenou",
        contact_heading: "Vine a Veure'ns a Poblenou",
        day_tue_fri: "Dimarts a Divendres",
        day_sat: "Dissabte",
        day_sun_mon: "Diumenge & Dilluns",
        closed_label: "Tancat per descans",
        cta_sticky_mobile: "Demanar Cita",
        wa_text: "Hola Mojo Perruqueria, voldria demanar cita"
      },
      es: {
        nav_concept_label: "CONCEPTO",
        nav_services_label: "SERVICIOS",
        nav_gallery_label: "GALERÍA",
        nav_contact_label: "CONTACTO",
        cta_header: "Pedir Cita",
        hero_title: "Donde tu MOJO encuentra su máxima expresión.",
        hero_description: "Inspirados en el blues americano y la estética cinematográfica. Entendemos cada servicio como una experiencia personalizada, conducida con mucho amor y sin prisas, con profesionalidad y complicidad en el corazón de Poblenou.",
        hero_cta_wa: "Reservar por WhatsApp",
        stat_years: "Años de Oficio",
        stat_unisex: "Unisex & Autor",
        stat_location: "C/ Llull 84, BCN",
        concept_heading: "¿Qué es el <span class='font-typewriter text-mojo-powder'>MOJO</span>?",
        concept_p1: "El concepto de <strong>MOJO</strong>, inspirado en el blues americano, es la cualidad o habilidad de atraer a la gente hacia ti, esa esencia tan preciada que solo poseen las personas más carismáticas.",
        concept_p2: "En nuestro espacio contamos con un equipo formado por los mejores profesionales que sacarán el máximo partido de todas tus cualidades. Nos gusta pensar nuestros servicios como una experiencia personalizada, conducida con mucho amor y poca prisa, con profesionalidad y complicidad.",
        concept_p3: "Ven a vernos y disfruta de nuestro acogedor espacio en el fantástico barrio de Poblenou, donde podrás compartir con nosotros pasiones como la música o el cine, de donde proceden la gran mayoría de nuestras influencias.",
        feat_1_title: "Influencia Musical & Blues",
        feat_1_desc: "Ambiente cálido con banda sonora cuidada",
        feat_2_title: "Sin Prisas, Con Amor",
        feat_2_desc: "Dedicación exclusiva para cada cliente",
        spotify_cta: "Abrir Playlist en Spotify",
        alex_role: "Fundador & Front Man de Mojo Perruquería",
        alex_p1: "Nuestro <em>front man</em>, <strong>Àlex Sans</strong>, cuenta con una carrera de más de 25 años vinculada al mundo de la estética.",
        alex_p2: "Ha trabajado tanto en reconocidos salones de peluquería como en el mundo audiovisual, ejerciendo como peluquero y estilista en <strong>cine, teatro, publicidad, televisión y pasarelas de moda</strong>.",
        alex_quote: '"Ahora ha llegado el momento de compartir su propio proyecto, una peluquería de autor donde vuestro MOJO estará en las mejores manos."',
        services_heading: "Cortes, Color & Cuidados Personalizados",
        services_subheading: "Técnicas precisas adaptadas a la textura de tu cabello y a tu personalidad. Selecciona un servicio para pedir cita directa.",
        srv_1_name: "Corte Unisex de Autor",
        srv_1_desc: "Asesoramiento morfológico personalizado, lavado con champú de tratamiento, corte a mano alzada o navaja y secado/estilismo natural.",
        srv_2_name: "Colorimetría & Balayage Creativo",
        srv_2_desc: "Técnicas de mechas, degradados suaves, babylights o cobertura total con productos respetuosos con la fibra capilar.",
        srv_3_name: "Ritual de Reconstrucción Capilar",
        srv_3_desc: "Tratamiento intensivo de ácido hialurónico y proteínas orgánicas para devolver brillo, elasticidad y fuerza al cabello dañado.",
        srv_4_name: "Peinado Editorial & Eventos",
        srv_4_desc: "Estilismo profesional para rodajes, sesiones de fotos, bodas o eventos especiales con sello de autor cinematográfico.",
        srv_5_name: "Baño de Color & Gloss Brillo",
        srv_5_desc: "Revivir el tono, neutralizar reflejos no deseados y aportar un baño de luz intenso sin alterar la base natural.",
        srv_6_name: "Afeitado Clásico & Arreglo de Barba",
        srv_6_desc: "Ritual con toalla caliente, perfilado con navaja tradicional, hidratación con aceites esenciales y masaje facial.",
        gallery_heading: "El Espacio & Los Trabajos en Poblenou",
        contact_heading: "Ven a Vernos a Poblenou",
        day_tue_fri: "Martes a Viernes",
        day_sat: "Sábado",
        day_sun_mon: "Domingo & Lunes",
        closed_label: "Cerrado por descanso",
        cta_sticky_mobile: "Pedir Cita",
        wa_text: "Hola Mojo Peluqueria, quisiera pedir cita"
      }
    };

    let currentLang = 'ca';

    function setLanguage(lang) {
      currentLang = lang;
      const dict = translations[lang] || translations.ca;

      // Update active toggle buttons
      const btnCa = document.getElementById('lang-btn-ca');
      const btnEs = document.getElementById('lang-btn-es');
      if (lang === 'ca') {
        btnCa.className = "px-2.5 py-1 rounded bg-mojo-powder text-mojo-black font-bold transition-all duration-150";
        btnEs.className = "px-2.5 py-1 rounded text-neutral-400 hover:text-white transition-all duration-150";
      } else {
        btnEs.className = "px-2.5 py-1 rounded bg-mojo-powder text-mojo-black font-bold transition-all duration-150";
        btnCa.className = "px-2.5 py-1 rounded text-neutral-400 hover:text-white transition-all duration-150";
      }

      // Update text nodes with data-i18n attribute
      document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
          el.innerHTML = dict[key];
        }
      });

      // Update WhatsApp links
      const waEncoded = encodeURIComponent(dict.wa_text);
      const waLink = `https://wa.me/34932440276?text=${waEncoded}`;
      
      const headerCta = document.getElementById('header-cta-btn');
      if (headerCta) headerCta.href = waLink;

      const heroCta = document.getElementById('hero-main-cta');
      if (heroCta) heroCta.href = waLink;

      const mobileCta = document.getElementById('mobile-sticky-cta');
      if (mobileCta) mobileCta.href = waLink;
    }

    // Filter Services Menu
    function filterServices(category) {
      const items = document.querySelectorAll('.service-item');
      items.forEach(item => {
        if (category === 'all' || item.getAttribute('data-category') === category) {
          item.style.display = 'flex';
        } else {
          item.style.display = 'none';
        }
      });

      // Update active tab buttons
      ['all', 'tall', 'color', 'ritual'].forEach(tab => {
        const btn = document.getElementById(`tab-${tab}`);
        if (btn) {
          if (tab === category) {
            btn.className = "px-4 py-2 rounded-lg bg-mojo-powder text-mojo-black font-bold transition";
          } else {
            btn.className = "px-4 py-2 rounded-lg bg-mojo-darkCard text-neutral-300 hover:text-white border border-mojo-darkBorder transition";
          }
        }
      });
    }

    // Real-Time Opening Hours Detection
    function updateOpeningHoursStatus() {
      const now = new Date();
      const day = now.getDay(); // 0 = Sun, 1 = Mon, 2 = Tue, ..., 6 = Sat
      const hour = now.getHours();
      const min = now.getMinutes();
      const curTime = hour + min / 60;

      const dot = document.getElementById('status-indicator-dot');
      const text = document.getElementById('status-text');
      const hint = document.getElementById('status-time-hint');

      if (!dot || !text || !hint) return;

      // Tuesday to Friday: 10:00 to 20:00
      if (day >= 2 && day <= 5) {
        if (curTime >= 10 && curTime < 20) {
          dot.className = "w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse";
          text.innerText = currentLang === 'ca' ? "Obert Ara" : "Abierto Ahora";
          text.className = "text-green-400 font-bold";
          hint.innerText = (currentLang === 'ca' ? "Tanca a les 20:00h" : "Cierra a las 20:00h");
        } else {
          dot.className = "w-2.5 h-2.5 rounded-full bg-amber-400";
          text.innerText = currentLang === 'ca' ? "Tancat en aquest moment" : "Cerrado en este momento";
          text.className = "text-neutral-300 font-bold";
          hint.innerText = (currentLang === 'ca' ? "Obre demà a les 10:00h" : "Abre mañana a las 10:00h");
        }
      } else if (day === 6) { // Saturday: 10:00 to 14:00
        if (curTime >= 10 && curTime < 14) {
          dot.className = "w-2.5 h-2.5 rounded-full bg-green-400 animate-pulse";
          text.innerText = currentLang === 'ca' ? "Obert Ara" : "Abierto Ahora";
          text.className = "text-green-400 font-bold";
          hint.innerText = (currentLang === 'ca' ? "Tanca a les 14:00h" : "Cierra a las 14:00h");
        } else {
          dot.className = "w-2.5 h-2.5 rounded-full bg-neutral-500";
          text.innerText = currentLang === 'ca' ? "Tancat" : "Cerrado";
          text.className = "text-neutral-400 font-bold";
          hint.innerText = (currentLang === 'ca' ? "Obre dimarts a les 10:00h" : "Abre martes a las 10:00h");
        }
      } else { // Sunday (0) & Monday (1)
        dot.className = "w-2.5 h-2.5 rounded-full bg-neutral-500";
        text.innerText = currentLang === 'ca' ? "Tancat per descans" : "Cerrado por descanso";
        text.className = "text-neutral-400 font-bold";
        hint.innerText = (currentLang === 'ca' ? "Obre dimarts a les 10:00h" : "Abre martes a las 10:00h");
      }
    }

    document.addEventListener('DOMContentLoaded', () => {
      updateOpeningHoursStatus();
    });
  </script>

</body>
</html>
"""

print(f"Deploying bespoke Mojo Perruqueria redesign for slug: {slug}...")

# 1. Sincronizar directamente con la rama gh-pages (0 MB en local)
res = sincronizar_gh_pages(slug=slug, html_content=html_content, accion="guardar")
print(f"✓ Sincronización con GitHub Pages completada: {res}")

# 2. Actualizar metadatos en data/leads.json
leads = leer_leads_guardados()
lead_found = False
for l in leads:
    if l.get("demo_slug") == slug or "manau" in l.get("nombre", "").lower():
        l["nombre"] = "Mojo Perruquería (Perruqueria Manau)"
        l["demo_slug"] = slug
        l["demo_vibe"] = "Mojo Perruquería Bespoke (Blues, Cinema & Typewriter)"
        l["web_detectada"] = "https://mojoperruqueria.com"
        l["telefono"] = "932440276"
        l["direccion"] = "Carrer de Llull 84, 08005 Barcelona"
        l["mensaje_dm"] = (
            "¡Hola equipo de Mojo Perruquería!\n\n"
            "Soy Daniel García. He visto vuestro gran trabajo y vuestra web actual (https://mojoperruqueria.com), "
            "y os he preparado una propuesta de rediseño y modernización mobile-first manteniendo al 100% vuestra estética "
            "(tipografía Courier, colores azul polvo y negro, y concepto de autor con Àlex Sans):\n\n"
            f"👉 https://dga80.github.io/instaleads/{slug}/\n"
            "*(Enlace 100% seguro para abrirlo cómodamente en el móvil sin descargas)*.\n\n"
            "¿Qué os parece la propuesta? Si os encaja, podemos comentarlo 2 minutos sin compromiso.\n\n"
            "Un saludo cordial,\n"
            "Daniel García | Diseño UX/UI & Desarrollo Frontend (Barcelona)\n"
            "🌐 https://dga-creative.netlify.app/"
        )
        l["mensaje_seguimiento"] = (
            "¡Hola de nuevo equipo de Mojo Perruquería!\n\n"
            f"Os escribí hace un par de días con la propuesta de rediseño mobile-first que preparé para vosotros: https://dga80.github.io/instaleads/{slug}/\n\n"
            "Os la comparto de nuevo por si se os pasó y queréis revisarla desde el móvil.\n\n"
            "¿Tenéis 2 minutos esta semana para comentarlo sin compromiso?\n\n"
            "Un saludo cordial,\n"
            "Daniel García | Diseño UX/UI & Desarrollo Frontend (Barcelona)\n"
            "🌐 https://dga-creative.netlify.app/"
        )
        lead_found = True
        break

if lead_found:
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    print("✓ Lead actualizado en data/leads.json")

print(f"🎉 Rediseño completado y publicado en: https://dga80.github.io/instaleads/{slug}/")
