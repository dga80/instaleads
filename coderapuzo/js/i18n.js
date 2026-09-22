/**
 * Internationalization (i18n) engine for Luis Codera Puzo
 * Bilingual: English (default) & Spanish
 */

(function () {
  'use strict';

  var translations = {
    en: {
      // Rail
      'rail.0': '0 — Ground',
      'rail.1': 'I — Activities',
      'rail.2': 'II — Biography',
      'rail.3': 'III — Works',
      'rail.4': 'IV — Modular Synth',
      'rail.5': 'V — Curator',
      'rail.6': 'VI — Essays',
      'rail.7': 'VII — Records',

      // Hero
      'hero.kicker': 'Luis Codera Puzo <span class="deg">· Barcelona, 1981 · Music & Thought</span>',
      'hero.title': 'Radical distillation. Sound as physical reality.',
      'hero.lede': 'Composer, performer of modular synthesizers and electric guitar, curator. From one of the first concertos for modular synthesizer and orchestra to the ascetic economy of unison: the electronic instrument approached with the performative discipline and tactile precision of a classical instrument.',
      'hero.hint': 'Scroll to ascend through the chapters <span class="arr">↓</span> eight rooms, from the oscillator to the score and ideas. Behind you, an analog wave settles into structure.',

      // Activities
      'act.kicker': 'I <span class="deg">· Agenda & Upcoming</span>',
      'act.title': 'Next and recent activities (selection).',
      'act.intro': 'Works in progress, solo modular synthesizer concert tours, and monographic recordings:',
      'act.item1.title': 'Las enumeraciones <span class="tag">SOLO SYNTH</span>',
      'act.item1.desc': 'Concert tour for solo analog modular synthesizer: Dimecres de so i cos (Art Santa Mònica, Barcelona), Tiny Moon (M33, Strasbourg), ME_MMIX (Palma de Mallorca), Cicle Difraccions (Lo Pati, Amposta and Tecla Sala, Hospitalet).',
      'act.item2.title': 'Cantus Firmus <span class="tag">PREMIERE</span>',
      'act.item2.desc': 'Electronic music installation for 8 loudspeakers placed across the forest. Fonz (Huesca).',
      'act.item3.title': 'Monographic recording of MUR#01 <span class="tag">NEU RECORDS</span>',
      'act.item3.desc': 'For 3 percussionists and modular synthesizers. Monographic album with Neu Records.',
      'act.item4.title': 'SUMMA#01 & SUMMA#02 <span class="tag">NEU RECORDS</span>',
      'act.item4.desc': 'For acoustic instruments and live electronics. 3D spatial high-fidelity release.',
      'act.item5.title': 'Transistor <span class="tag">SPACESHIP ENSEMBLE</span>',
      'act.item5.desc': 'For modular synthesizer and chamber group. Premiered in The Hague and Utrecht.',
      'act.item6.title': 'New piece for Collective Lovemusic <span class="tag">2027</span>',
      'act.item6.desc': 'For 4 musicians and modular synthesizer.',
      'act.item7.title': 'New piece for oboe and synthesizer <span class="tag">2027</span>',
      'act.item7.desc': 'Chamber commission exploring direct acoustic-synthetic timbral interaction.',
      'act.item8.title': 'Exhale. Inhale. Exile <span class="tag">2026–2028</span>',
      'act.item8.desc': 'For piano, modular synthesizer, sampler and drum machine (45′).',
      'act.plate': '<b>The instrument in live performance.</b> Subtractive and microtonal modular synthesis — pure physical performativity, zero canned sequences.',

      // Bio
      'bio.kicker': 'II <span class="deg">· Trajectory & Education</span>',
      'bio.title': 'Clarity, distillation, and critical listening.',
      'bio.p1': 'Luis Codera Puzo (Barcelona, 1981) is a composer, cultural manager, and performer of modular synthesizers and electric guitar. He has stood out for his active dedication to the modular synthesizer as a solo and chamber concert instrument, developing an instrumental technique focused on performativity and precise micro-interaction with other musicians. This approach has led to pioneering works such as <em>MUR#03</em>, one of the first concertos for modular synthesizer and orchestra (premiered by the OBC – Barcelona Symphony Orchestra), and <em>Compression Music</em>, created with support from the Leonardo Grants of the BBVA Foundation.',
      'bio.p2': 'Acoustic music has also played a defining role in his career, oriented toward clarity and the idea in its most distilled form. Works such as <em>Code is poetry</em> (premiered by Quatuor Diotima at the Barcelona String Quartet Biennale) make use of unisons, repeated notes, and monolithic writing to open space for listening and bring out microscopic acoustic details that often go unnoticed — such as instrument beating and natural string vibrato.',
      'bio.stat.num': 'Ernst von Siemens',
      'bio.stat.desc': 'Composition Prize of the Ernst von Siemens Musikstiftung (2014) and guest composer of L’Auditori de Barcelona (2017).',
      'bio.p3': 'Initially self-taught, he studied piano, trombone, electric guitar, and percussion before graduating in composition at ESMuC (with Agustí Charles) and completing the Solistenexam with <strong>Wolfgang Rihm</strong> at the Hochschule für Musik Karlsruhe. He has participated in masterclasses with Louis Andriessen, Kaija Saariaho, Enno Poppe, Beat Furrer, Georg Friedrich Haas, Unsuk Chin, and Pierluigi Billone. His music has been performed worldwide by Klangforum Wien, Ensemble Modern, Ensemble Intercontemporain, Quatuor Diotima, and ensemble recherche.',
      'bio.plate1': '<b>MUR#03 at L’Auditori.</b> Modular synthesizer and symphony orchestra with the OBC.',
      'bio.plate2': '<b>Electric guitar & electronics.</b> Timbral research, pedals, and dynamic control.',

      // Works Catalogue
      'cat.kicker': 'III <span class="deg">· Catalogue of Works</span>',
      'cat.title': 'A rigorous catalogue.',
      'cat.intro': 'Chamber, orchestra, solo instrument, and spatial electronics, categorized by ensemble:',
      'cat.filter.all': 'All',
      'cat.filter.chamber': 'Chamber & Ensemble',
      'cat.filter.orchestra': 'Orchestra',
      'cat.filter.solo': 'Solo & Synthesizer',
      'cat.filter.special': 'Special Projects',
      'cat.btn.listen': '▶ Watch recording',
      'cat.btn.sc': '▶ Listen on SoundCloud',
      'cat.btn.read': 'Read work essay',
      'cat.spec.title': 'Microtonal Pitch Matrix · <code>MUR#02</code> (3 tuned pianos)',
      'cat.spec.note': 'Non-tempered acoustic tunings generating continuous interference and beating patterns in physical space.',
      'cat.plate.mur': '<b>MUR#01.</b> Percussion and electronics.',
      'cat.plate.diotima': '<b>Quatuor Diotima.</b> Premiere of <em>Code is poetry</em>.',
      'cat.plate.cip': '<b>Score.</b> <em>Code is poetry</em> (distilled notation).',
      'cat.plate.pletora': '<b>Plétora.</b> Electric study 1.',
      'cat.plate.empor': '<b>Empor.</b> Spatialized listening.',

      // Modular Synth
      'syn.kicker': 'IV <span class="deg">· The Modular Synthesizer · Manifesto & Technique</span>',
      'syn.title': 'We don’t need more synthesizers; we need discipline.',
      'syn.p1': 'One of the most evident dangers in contemporary electronic music lies in the <strong>fetishistic consideration of the instrument</strong>: the machine exhibited as an advertising slogan or a visual fetish rather than as a rigorous medium of musical articulation.',
      'syn.p2': 'The modular synthesizer is not a toy for random bleeps or automated effects. It is a <strong>physical concert instrument</strong> where every cable, attenuator, and voltage must answer to the same interpretative discipline as the bow of a violin or the embouchure of a flute. We play with our hands, shaping envelope, dynamics, and breath in real time.',
      'syn.spec.title': 'Modular Voice Architecture · Performative Control Patch',
      'syn.spec.note': 'Zero presets or external automation: tactile, direct manual control over gain and timbral cutoff.',
      'syn.plate1': '<b>The live system.</b> Eurorack panels and subtractive architecture.',
      'syn.plate2': '<b>Voltage and routing.</b> Every patch cord defines the physical acoustics of the work.',
      'syn.btn.play': '▶&nbsp;hear the synthesizer harmonic tone series',
      'syn.playnote': 'Eight harmonic tones based on just intonation ratios and analog intervals. Computed entirely via Web Audio API on your machine, zero external audio files.',

      // Curator
      'cur.kicker': 'V <span class="deg">· Curation & Artistic Structures</span>',
      'cur.title': 'Putting ideology into practice.',
      'cur.intro': 'Curating and managing projects linked to new music is not an administrative add-on, but an <strong>actively critical</strong> way of engaging with the inertia of our cultural environment.',
      'cur.item1.title': 'OUT·SIDE (2016–2023) <span class="tag">CONCERT SERIES</span>',
      'cur.item1.desc': 'Pioneering series of unusual music in contemporary art centers across Catalonia (Arts Santa Mònica, Tecla Sala, Lo Pati in Amposta, Bòlit in Girona). Territorial decentralization and dialogue with visual arts.',
      'cur.item2.title': 'CrossingLines Ensemble (2009–2017) <span class="tag">FOUNDER & DIRECTOR</span>',
      'cur.item2.desc': 'Founding and artistic direction of the reference contemporary music ensemble in Barcelona, premiering dozens of works while championing fair remuneration and professional dignity.',
      'cur.item3.title': 'FRAMES Percussion <span class="tag">STRATEGIC ADVISOR</span>',
      'cur.item3.desc': 'Institutional and project advisory for the percussion group, recently awarded the prestigious Ensemble Prize from the Ernst von Siemens Musikstiftung.',
      'cur.item4.title': 'Fair Working Conditions <span class="tag">CORE PRINCIPLE</span>',
      'cur.item4.desc': 'Ethical commitment to transparent budgets, dignified fees, and defending cultural workers against systemic precarity.',
      'cur.plate.cl': '<b>CrossingLines.</b> Contemporary music ensemble of Barcelona.',
      'cur.plate.outside18': '<b>OUT·SIDE ’18.</b> Unusual music in art spaces.',
      'cur.plate.tecla': '<b>Tecla Sala.</b> Immersive performance in the art center.',
      'cur.quote': '<em>«Listening rigorously to the music of others is the primary condition for being able to write one’s own.»</em>',

      // Essays
      'ide.kicker': 'VI <span class="deg">· Ideas, Texts & Essays</span>',
      'ide.title': 'Text as an extension of musical thought.',
      'ide.intro': 'A selection of aesthetic, technical, and sociological essays written by Luis Codera Puzo. Click any card to open the typography-focused reader:',
      'ide.card.electronic': 'Live modular synthesis approached from the perspective and discipline of classical instrumental training.',
      'ide.card.synths': 'A critique of material fetishism in electronic music and a call for performative dedication.',
      'ide.card.belonging': 'Deconstructing the commonplaces of the composer guild and the trap of "being oneself".',
      'ide.card.code': 'On the premiere by Quatuor Diotima and how the use of musical codes reveals the nature of listening.',
      'ide.card.indivisible': 'An extensive treatise on unifying timbre, pitch, and duration in contemporary acoustic composition.',
      'ide.card.compression': 'BBVA Leonardo research project: dynamic compression, acoustic mass, and modular synthesis.',
      'ide.card.patience': 'Cultural acceleration and the loss of the capacity to sustain prolonged attention in time.',
      'ide.card.guild': 'An incisive sociological analysis of power structures and networking in the contemporary music scene.',
      'ide.card.narrative': 'Critical reflection on institutional storytelling and identity construction in Catalan composition.',
      'ide.card.tonality': 'Notes on the nostalgic return to tonality versus conquering irreducible sonic specificity.',
      'ide.card.zoology': 'Fiction and ethnographic cataloguing of imaginary acoustic animal species.',
      'ide.card.hideouts': 'Sonic sanctuary, acoustic memory, and deep listening between space and isolation.',
      'ide.card.white': 'White as the saturation of all acoustic frequencies and a space of pure neutrality.',
      'ide.card.laws': 'Condensed aphorisms on acoustics, material behavior, and the boundaries of authorship.',
      'ide.readmore': 'Read essay →',

      // Records
      'rec.kicker': 'VII <span class="deg">· Discography & Contact</span>',
      'rec.title': 'Sound fixed in time.',
      'rec.intro': 'Monographic recordings and releases with independent high-fidelity labels:',
      'rec.mur1': '3 percussionists + modular synthesizer',
      'rec.summa': 'SUMMA#01 & SUMMA#02',
      'rec.albedo': 'Piano and electronics',
      'rec.multi': 'Monographic chamber portrait',
      'rec.feldman': 'Bass Clarinet & Percussion (Artistic direction)',
      'rec.contact.title': 'Contact & Links',
      'rec.contact.desc': 'For inquiries regarding commissions, scores, performances, or lectures:',
      'rec.return': '↑ return to Ground (0 · Ground)',

      // Footer & General
      'footer.copy': '© 2026 Luis Codera Puzo · <a href="https://coderapuzo.com">coderapuzo.com</a><br>From 0 to VII — All sound synthesis and graphics on this page happen locally on your machine.',
      'modal.close': '✕ Close [Esc]',
      'modal.kicker': 'Luis Codera Puzo · Ideas & Essays',
      'modal.links': 'Related links:'
    },

    es: {
      // Rail
      'rail.0': '0 — El suelo sonoro',
      'rail.1': 'I — Actividad reciente',
      'rail.2': 'II — Biografía & trayectoria',
      'rail.3': 'III — Catálogo de obras',
      'rail.4': 'IV — El sintetizador modular',
      'rail.5': 'V — Comisariado & estructuras',
      'rail.6': 'VI — Ensayos & biblioteca',
      'rail.7': 'VII — Discografía & contacto',

      // Hero
      'hero.kicker': 'Luis Codera Puzo <span class="deg">· Barcelona, 1981 · Música y Pensamiento</span>',
      'hero.title': 'Destilación radical. El sonido como materia física.',
      'hero.lede': 'Compositor, intérprete de sintetizadores modulares y guitarra eléctrica, comisario. Del concierto para sintetizador modular y orquesta a la economía ascética del unísono: el instrumento electrónico abordado con la disciplina performativa y la precisión táctil de un instrumento clásico.',
      'hero.hint': 'Desplaza para ascender por los capítulos <span class="arr">↓</span> ocho estancias, del oscilador al catálogo y los textos. Detrás, una onda analógica se decanta en estructura.',

      // Activities
      'act.kicker': 'I <span class="deg">· Agenda & Estrenos</span>',
      'act.title': 'Actividad reciente y futuros proyectos.',
      'act.intro': 'Obras en creación, conciertos de sintetizador modular solista y grabaciones discográficas monográficas en curso:',
      'act.item1.title': 'Las enumeraciones <span class="tag">SOLO SYNTH</span>',
      'act.item1.desc': 'Gira del programa para sintetizador analógico solo: Dimecres de so i cos (Art Santa Mònica, Barcelona), Tiny Moon (M33, Estrasburgo), ME_MMIX (Palma de Mallorca), Cicle Difraccions (Lo Pati, Amposta y Tecla Sala, Hospitalet).',
      'act.item2.title': 'Cantus Firmus <span class="tag">ESTRENO</span>',
      'act.item2.desc': 'Instalación de música electrónica para 8 altavoces distribuidos en el bosque. Fonz (Huesca).',
      'act.item3.title': 'Grabación monográfica MUR#01 <span class="tag">NEU RECORDS</span>',
      'act.item3.desc': 'Para 3 percusionistas y sintetizadores modulares. Grabación y edición monográfica con el sello Neu Records.',
      'act.item4.title': 'SUMMA#01 & SUMMA#02 <span class="tag">NEU RECORDS</span>',
      'act.item4.desc': 'Para instrumentos acústicos y electrónica en vivo. Lanzamiento en formato espacial de alta fidelidad.',
      'act.item5.title': 'Transistor <span class="tag">SPACESHIP ENSEMBLE</span>',
      'act.item5.desc': 'Para sintetizador modular y grupo de cámara. Estreno en La Haya y Utrecht.',
      'act.item6.title': 'Nueva obra para Collective Lovemusic <span class="tag">2027</span>',
      'act.item6.desc': 'Para 4 músicos y sintetizador modular.',
      'act.item7.title': 'Nueva obra para oboe y sintetizador <span class="tag">2027</span>',
      'act.item7.desc': 'Encargo camerístico de interacción tímbrica directa entre acústica y síntesis.',
      'act.item8.title': 'Exhale. Inhale. Exile <span class="tag">2026–2028</span>',
      'act.item8.desc': 'Para piano, sintetizador modular, sampler y caja de ritmos (45′).',
      'act.plate': '<b>El instrumento en escena.</b> Síntesis modular sustractiva y microtonal — performatividad en vivo, sin secuenciación enlatada.',

      // Bio
      'bio.kicker': 'II <span class="deg">· Trayectoria & Formación</span>',
      'bio.title': 'Claridad, destilación y escucha crítica.',
      'bio.p1': 'Luis Codera Puzo (Barcelona, 1981) se ha distinguido por su dedicación activa al sintetizador modular como instrumento de concierto solista y camerístico. Su técnica instrumental, orientada a la performatividad y a la interacción milimétrica con instrumentistas acústicos, ha dado lugar a obras pioneras como <em>MUR#03</em> —uno de los primeros conciertos para sintetizador modular y orquesta, estrenado por la Orquestra Simfònica de Barcelona i Nacional de Catalunya (OBC)— o <em>Compression Music</em>, creada con una Beca Leonardo de la Fundación BBVA.',
      'bio.p2': 'Su música acústica se orienta hacia la forma más destilada de la idea. Piezas como <em>Code is poetry</em> (estrenada por el Quatuor Diotima en la Bienal de Cuartetos de Barcelona) hacen uso de unísonos, notas repetidas y una escritura monolítica que ensancha el espacio de escucha para visibilizar matices microscópicos, como el batimiento o el vibrato natural de las cuerdas.',
      'bio.stat.num': 'Ernst von Siemens',
      'bio.stat.desc': 'Premio de Composición de la Fundación Ernst von Siemens (2014) y compositor invitado de L\'Auditori de Barcelona (2017).',
      'bio.p3': 'Formado inicialmente de manera autodidacta, estudió piano, trombón, guitarra eléctrica y percusión antes de titularse en composición en la ESMuC (con Agustí Charles) y realizar el Solistenexam con <strong>Wolfgang Rihm</strong> en la Hochschule für Musik Karlsruhe. Ha recibido clases y seminarios de compositores como Louis Andriessen, Kaija Saariaho, Enno Poppe, Beat Furrer, Georg Friedrich Haas, Unsuk Chin y Pierluigi Billone. Su música ha sido interpretada en festivales internacionales por Klangforum Wien, Ensemble Modern, Ensemble Intercontemporain, Quatuor Diotima y ensemble recherche.',
      'bio.plate1': '<b>MUR#03 en L’Auditori.</b> Sintetizador modular y orquesta sinfónica con la OBC.',
      'bio.plate2': '<b>Guitarra eléctrica & electrónica.</b> Investigación de texturas, pedales y control tímbrico.',

      // Works Catalogue
      'cat.kicker': 'III <span class="deg">· Catálogo de Obras</span>',
      'cat.title': 'Un catálogo riguroso.',
      'cat.intro': 'Obras de cámara, orquesta, instrumento solo y electrónica espacial, ordenadas por orgánico:',
      'cat.filter.all': 'Todas',
      'cat.filter.chamber': 'Cámara & Ensemble',
      'cat.filter.orchestra': 'Orquesta',
      'cat.filter.solo': 'Solo & Sintetizador',
      'cat.filter.special': 'Proyectos Especiales',
      'cat.btn.listen': '▶ Ver grabación',
      'cat.btn.sc': '▶ Escuchar en SoundCloud',
      'cat.btn.read': 'Leer texto de la obra',
      'cat.spec.title': 'Ficha de microafinación · <code>MUR#02</code> (3 pianos afinados)',
      'cat.spec.note': 'Afinaciones acústicas no temperadas generando patrones de interferencia pura en el espacio.',
      'cat.plate.mur': '<b>MUR#01.</b> Percusión y electrónica.',
      'cat.plate.diotima': '<b>Quatuor Diotima.</b> Estreno de <em>Code is poetry</em>.',
      'cat.plate.cip': '<b>Partitura.</b> <em>Code is poetry</em> (notación destilada).',
      'cat.plate.pletora': '<b>Plétora.</b> Estudio eléctrico 1.',
      'cat.plate.empor': '<b>Empor.</b> Escucha espacializada.',

      // Modular Synth
      'syn.kicker': 'IV <span class="deg">· El Sintetizador Modular · Manifiesto y Técnica</span>',
      'syn.title': 'No necesitamos más sintetizadores: necesitamos disciplina.',
      'syn.p1': 'Uno de los peligros más evidentes en la música electrónica contemporánea reside en la <strong>consideración fetichista del instrumento</strong>: el aparato exhibido como un eslogan publicitario o un fetiche visual antes que como un medio riguroso de articulación musical.',
      'syn.p2': 'El sintetizador modular no es un juguete de aleatoriedades sonoras o efectos automáticos. Es un <strong>instrumento físico de concierto</strong> donde cada cable, cada atenuador y cada voltaje debe responder a la misma disciplina interpretativa que el arco de un violín o la embocadura de una flauta. Tocamos con los dedos, controlando la envolvente, el tiempo y la respiración en tiempo real.',
      'syn.spec.title': 'Arquitectura de voz modular · Patch de control performativo',
      'syn.spec.note': 'Sin presets ni automatizaciones externas: control táctil y manual de la ganancia y el corte tímbrico.',
      'syn.plate1': '<b>El sistema en directo.</b> Paneles Eurorack y arquitectura sustractiva.',
      'syn.plate2': '<b>Voltaje y ruteo.</b> Cada conexión define la física acústica de la pieza.',
      'syn.btn.play': '▶&nbsp;escuchar la serie de tonos del sintetizador',
      'syn.playnote': 'Ocho tonos armónicos basados en relaciones justas e intervalos analógicos. Generados íntegramente mediante Web Audio API en tu navegador, sin grabaciones externas.',

      // Curator
      'cur.kicker': 'V <span class="deg">· Comisariado & Estructuras</span>',
      'cur.title': 'Poner la ideología en práctica.',
      'cur.intro': 'El comisariado y la gestión de proyectos ligados a la nueva música no son un añadido administrativo, sino la forma de ser <strong>activamente crítico</strong> con las inercias del entorno cultural y musical.',
      'cur.item1.title': 'OUT·SIDE (2016–2023) <span class="tag">CICLO DE CONCIERTOS</span>',
      'cur.item1.desc': 'Ciclo pionero de músicas inusuales en centros de arte contemporáneo de Cataluña (Arts Santa Mònica, Centre d\'Art Tecla Sala, Lo Pati en Amposta, Bòlit en Girona). Descentralización territorial y diálogo estrecho con las artes plásticas.',
      'cur.item2.title': 'Ensemble CrossingLines (2009–2017) <span class="tag">FUNDADOR Y DIRECTOR</span>',
      'cur.item2.desc': 'Creación y dirección artística del ensemble referente de música contemporánea en Barcelona, estrenando decenas de obras y defendiendo la remuneración digna y la profesionalización de intérpretes y compositores.',
      'cur.item3.title': 'FRAMES Percussion <span class="tag">ASESORAMIENTO ESTRATÉGICO</span>',
      'cur.item3.desc': 'Acompañamiento institucional y de proyectos para el ensemble de percusión, recientemente galardonado con el Ensemble Prize de la Ernst von Siemens Musikstiftung.',
      'cur.item4.title': 'Condiciones laborales justas <span class="tag">PRINCIPIO</span>',
      'cur.item4.desc': 'Compromiso ético con la transparencia económica, presupuestos dignos y la defensa de los derechos profesionales de los trabajadores de la cultura frente a la precarización endémica.',
      'cur.plate.cl': '<b>CrossingLines.</b> Ensemble de música contemporánea de Barcelona.',
      'cur.plate.outside18': '<b>OUT·SIDE ’18.</b> Músicas inusuales en centros de arte.',
      'cur.plate.tecla': '<b>Tecla Sala.</b> Concierto inmersivo en el centro de arte.',
      'cur.quote': '<em>«Escuchar la música de los demás con rigor es la primera condición para poder escribir la propia.»</em>',

      // Essays
      'ide.kicker': 'VI <span class="deg">· Ideas, Textos y Ensayos</span>',
      'ide.title': 'El texto como extensión del pensamiento sonoro.',
      'ide.intro': 'Una selección de los artículos y ensayos de reflexión estética, técnica y sociológica escritos por Luis Codera Puzo. Haz clic en cualquier tarjeta para abrir el lector inmersivo integrado:',
      'ide.card.electronic': 'El uso del sintetizador modular desde la perspectiva y la disciplina del entrenamiento instrumental clásico.',
      'ide.card.synths': 'Crítica al fetichismo del material en la música electrónica y defensa de la dedicación performativa.',
      'ide.card.belonging': 'Desmontando los lugares comunes del gremio de compositores y la trampa del eslogan «ser uno mismo».',
      'ide.card.code': 'Sobre el estreno de la obra por el Quatuor Diotima y cómo el uso del código revela la naturaleza de la escucha.',
      'ide.card.indivisible': 'Extenso tratado sobre la unificación de timbre, afinación y duración en la composición acústica contemporánea.',
      'ide.card.compression': 'La investigación financiada por la Beca Leonardo: compresión dinámica, acústica y electrónica en un solo cuerpo.',
      'ide.card.patience': 'La aceleración cultural y la pérdida de la capacidad de sostener una atención dilatada en el tiempo.',
      'ide.card.guild': 'Análisis incisivo sobre las estructuras de poder, redes de favores e inercias del entorno compositivo.',
      'ide.card.narrative': 'Reflexión crítica sobre el relato institucional y la construcción de identidades en la creación contemporánea.',
      'ide.card.tonality': 'Notas sobre el retorno nostálgico a la tonalidad frente a la conquista de una especificidad sonora irreductible.',
      'ide.card.zoology': 'Relato y exploración de especies sonoras ficticias catalogadas con rigor etnográfico.',
      'ide.card.hideouts': 'Refugio sonoro, memoria y escucha profunda entre el espacio y el aislamiento.',
      'ide.card.white': 'El color blanco como saturación de todas las frecuencias y espacio de neutralidad pura.',
      'ide.card.laws': 'Reflexiones condensadas sobre la acústica, el comportamiento de los materiales y los límites del autor.',
      'ide.readmore': 'Leer ensayo →',

      // Records
      'rec.kicker': 'VII <span class="deg">· Discografía & Contacto</span>',
      'rec.title': 'El sonido fijado en el tiempo.',
      'rec.intro': 'Grabaciones monográficas y lanzamientos en sellos independientes de alta fidelidad:',
      'rec.mur1': '3 percusionistas + sintetizador modular',
      'rec.summa': 'SUMMA#01 & SUMMA#02',
      'rec.albedo': 'Piano y electrónica',
      'rec.multi': 'Retrato monográfico de cámara',
      'rec.feldman': 'Bass Clarinet & Percussion (Dir. artística)',
      'rec.contact.title': 'Contacto & Redes',
      'rec.contact.desc': 'Consultas sobre encargos, partituras, interpretaciones o conferencias:',
      'rec.return': '↑ Volver al inicio (0 · El suelo sonoro)',

      // Footer & General
      'footer.copy': '© 2026 Luis Codera Puzo · <a href="https://coderapuzo.com">coderapuzo.com</a><br>De 0 a VII — Todo el sonido y los gráficos de esta página ocurren localmente en tu máquina.',
      'modal.close': '✕ Cerrar [Esc]',
      'modal.kicker': 'Luis Codera Puzo · Ideas & Ensayos',
      'modal.links': 'Enlaces relacionados:'
    }
  };

  var currentLang = 'en'; // Default English as requested

  function getSavedLang() {
    try {
      var saved = localStorage.getItem('coderapuzo_lang');
      if (saved && (saved === 'en' || saved === 'es')) return saved;
    } catch (e) {}
    return 'en'; // Default English
  }

  function setLanguage(lang) {
    if (!translations[lang]) return;
    currentLang = lang;
    document.documentElement.lang = lang;

    try {
      localStorage.setItem('coderapuzo_lang', lang);
    } catch (e) {}

    // Update active state on language buttons
    document.querySelectorAll('.lang-btn').forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
    });

    // Translate all elements with data-i18n
    var dict = translations[lang];
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      var key = el.getAttribute('data-i18n');
      if (dict[key]) {
        el.textContent = dict[key];
      }
    });

    // Translate all elements with data-i18n-html
    document.querySelectorAll('[data-i18n-html]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-html');
      if (dict[key]) {
        el.innerHTML = dict[key];
      }
    });

    // Translate aria labels or titles
    document.querySelectorAll('[data-i18n-aria]').forEach(function (el) {
      var key = el.getAttribute('data-i18n-aria');
      if (dict[key]) {
        el.setAttribute('aria-label', dict[key]);
      }
    });
  }

  // Initialize on load
  document.addEventListener('DOMContentLoaded', function () {
    var initial = getSavedLang();
    setLanguage(initial);

    // Language switch click handler
    document.addEventListener('click', function (e) {
      var btn = e.target.closest ? e.target.closest('.lang-btn') : null;
      if (btn) {
        var lang = btn.getAttribute('data-lang');
        if (lang && lang !== currentLang) {
          setLanguage(lang);
        }
      }
    });
  });

  window.I18n = {
    getLang: function () { return currentLang; },
    setLang: setLanguage,
    t: function (key) {
      return (translations[currentLang] && translations[currentLang][key]) || key;
    }
  };

})();
