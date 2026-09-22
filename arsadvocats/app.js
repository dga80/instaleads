/**
 * ARS ADVOCATS I ASSESSORS - Interactive Application Script
 * Features:
 * - Instant Bilingual Engine (Català / Castellà) with LocalStorage persistence
 * - Specialty Category Filter pills
 * - Scroll Reveal with IntersectionObserver
 * - Mobile Navigation Drawer
 * - Legal & Privacy Modals
 * - Contact Form validation & interactive feedback
 */

const translations = {
  ca: {
    top_address: "C/ Barcelona, 7 - 1r, Granollers",
    nav_presentation: "Presentació",
    nav_specialties: "Especialitats",
    nav_team: "L'Equip",
    nav_values: "Filosofia",
    nav_contact: "Contacte",
    nav_cta: "Demanar Cita",
    hero_badge: "Firma Legal a Granollers & Barcelona",
    hero_title_1: "Rigor, compromís",
    hero_title_2: "i excel·lència jurídica",
    hero_title_3: "al centre de Granollers.",
    hero_desc: "ARS Advocats i Assessors és un despatx modern, jove i àgil integrat per advocats de primer nivell. Aportem solucions pràctiques, sentit comú i una visió estratègica global per protegir els interessos de particulars i empreses.",
    hero_cta_consult: "Demanar Primera Consulta",
    hero_cta_specialties: "Explorar Àrees de Dret",
    hero_btn_explore: "Explorar Àrees de Dret",
    stat_areas: "Àrees d'especialització jurídica",
    stat_board: "Membres Junta de Govern & ICAB",
    stat_dedication: "Compromís ètic i atenció personalitzada",
    float_title: "Ubicació Estratègica",
    float_sub: "Carrer de Barcelona, 7 · Granollers",
    float_desc: "Atenció directa amb el soci responsable del teu cas.",
    badge_firm: "Firma d'Advocats Integral",
    badge_bw_to_color: "Clica per veure en color",
    badge_color_to_bw: "Color actiu · Clica per B/N",
    pres_kicker: "PRESENTACIÓ INSTITUCIONAL",
    pres_title_1: "Un despatx jove,",
    pres_title_2: "modern, àgil i compromès.",
    pres_p1: "ARS Advocats i Assessors som una firma d’advocats i d’assessorament legal integral, situada al centre històric i comercial de Granollers.",
    pres_p2: "El nostre és un despatx jove, modern i àgil, integrat per professionals altament compromesos i advocats de primer nivell. Aportem una àmplia experiència en totes les àrees d’especialització a què ens dediquem, amb una visió global que prioritza el servei, el rigor, la qualitat i el compromís ferm amb el client.",
    pres_p3: "Treballem amb passió, apostant constantment per la millora i la innovació. Creiem fermament en el sentit comú i en l’aplicació de solucions pràctiques i creatives que resolguin amb eficàcia els problemes i inquietuds legals, fent nostres els seus reptes.",
    pres_quote: "Per garantir un assessorament eficaç i de qualitat, considerem imprescindible conèixer en profunditat els nostres clients, així com els seus negocis i circumstàncies particulars.",
    pres_motto: "L'objectiu principal d'ARS es resumeix en una paraula: QUALITAT.",
    feat_1_title: "Sentit Comú & Creativitat",
    feat_1_desc: "Evitem solucions estàndard; dissenyem estratègies a mida per a cada conflicte.",
    feat_2_title: "Tracte Directe amb Socis",
    feat_2_desc: "Comunicació transparent, immediata i sense intermediaris innecessaris.",
    spec_kicker: "ÀREES DE PRÀCTICA JURÍDICA",
    spec_title: "Servei Integral en Dret Privat i Públic",
    spec_subtitle: "Ens dediquem a atendre i resoldre de forma eficaç, coherent i ètica qualsevol conflicte o necessitat legal plantejada per particulars, famílies i societats mercantils.",
    filter_all: "Totes les Àrees",
    filter_civil: "Civil & Família",
    filter_business: "Mercantil & Empresa",
    filter_criminal: "Penal",
    filter_labor: "Laboral & Danys",
    filter_property: "Immobiliari & Financer",
    sp_1_title: "Dret Matrimonial i de Família",
    sp_1_desc: "Processos de separació i divorci (de mutu acord o contenciós), redacció de convenis reguladors, guarda i custòdia, pensió d'aliments i modificació de mesures judicials.",
    sp_2_title: "Successions, Testaments i Herències",
    sp_2_desc: "Planificació successòria patrimonial, tramitació i acceptació d'herències davant notari, declaracions d'hereus, reclamació de legítima i impugnació de testaments.",
    sp_3_title: "Desnonaments i Arrendaments",
    sp_3_desc: "Recuperació ràpida de la possessió d'immobles per impagament de rendes o expiració de termini contractual. Redacció de contractes d'arrendament d'habitatge i local de negoci.",
    sp_4_title: "Obligacions i Contractes",
    sp_4_desc: "Redacció, interpretació i negociació de contractes civils i mercantils. Resolució per incompliment, reclamació de vicis ocults i indemnització de danys i perjudicis.",
    sp_5_title: "Reclamacions de Quantitat",
    sp_5_desc: "Reclamació extrajudicial i judicial d'impagats i deutes pendents. Procediments monitoris, ordinaris, verbals i execució d'actius i embargaments patrimonials.",
    sp_6_title: "Comunitats de Propietaris",
    sp_6_desc: "Assessorament en Propietat Horitzontal, impugnació d'acords comunitaris nuls o perjudicials, reclamació a veïns morosos i responsabilitat per defectes de construcció.",
    sp_7_title: "Dret Bancari & Clàusules Abusives",
    sp_7_desc: "Defensa davant abusos bancaris: clàusules sòl, despeses de formalització d'hipoteca, comissions abusives, targetes revolving i execucions hipotecàries.",
    sp_8_title: "Dret Penal & Defensa Judicial",
    sp_8_desc: "Assistència urgent al detingut a comissaria i jutjat de guàrdia. Defensa i acusació particular en procediments per delictes lleus, menys greus i greus.",
    sp_9_title: "Violència de Gènere",
    sp_9_desc: "Atenció especialitzada, urgent i sensible. Sol·licitud d'ordres de protecció i allunyament, mesures cautelars personals i patrimonials, i acompanyament en tot el procés penal.",
    sp_10_title: "Dret Econòmic & Compliance",
    sp_10_desc: "Prevenció de delictes corporatius (Corporate Compliance), responsabilitat penal de la persona jurídica, estafes, apropiacions indegudes i delictes societaris.",
    sp_11_title: "Accidents de Trànsit",
    sp_11_desc: "Defensa dels drets de les víctimes d'accidents de circulació. Càlcul precís de barems mèdics legals i màxima indemnització per danys materials, físics i seqüeles.",
    sp_12_title: "Dret Laboral & Seguretat Social",
    sp_12_desc: "Acomiadaments disciplinaris i objectius, reclamació de salaris, sancions laborals, expedients de regulació d'ocupació (ERO/ERTO) i representació en actes de conciliació (CMAC).",
    sp_13_title: "Procediments d'Incapacitat Laboral",
    sp_13_desc: "Tramitació i reclamació judicial de pensions per incapacitat laboral permanent (parcial, total, absoluta i gran invalidesa). Impugnació d'altes mèdiques de l'INSS i mútues.",
    sp_14_title: "Assessorament a Societats Mercantils",
    sp_14_desc: "Constitució d'empreses, redacció de pactes de socis, acords de confidencialitat, fusions, ampliacions de capital, secretària de consells i conflictes entre socis.",
    sp_15_title: "Concursos & Llei de Segona Oportunitat",
    sp_15_desc: "Reestructuració de deutes i insolvències per a pimes i autònoms. Aplicació de la Llei de la Segona Oportunitat per a la cancel·lació definitiva de deutes personals.",
    spec_cta_lead: "Necessites assessorament en una altra matèria o tens dubtes sobre la viabilitat del teu cas?",
    spec_cta_btn: "Consulta'ns sense compromís",
    team_kicker: "PROFESSIONALS DE PRIMER NIVELL",
    team_title: "L'Equip d'ARS Advocats",
    team_subtitle: "Un equip directiu cohesionat, compromès i accessible, amb sòlida formació a la Universitat de Barcelona i presència activa a les institucions col·legials.",
    team_role_partner: "Soci Director",
    team_role_collab: "Advocada Col·laboradora",
    roger_bio_1: "Llicenciat en Dret per la <strong>Universitat de Barcelona (UB)</strong>, amb Màster en Advocacia per l’<strong>Il·lustre Col·legi d’Advocats de Barcelona (ICAB)</strong>.",
    roger_bio_2: "S’encarrega i es responsabilitza de la direcció dels Departaments de <strong>Dret Civil</strong>, <strong>Dret de Família</strong> i <strong>Dret Penal</strong>.",
    roger_honor: "Membre de la Junta de Govern de l'ICAVOR (Granollers)",
    team_btn_contact: "Contactar",
    alex_bio_1: "Llicenciat en Dret per la <strong>Universitat de Barcelona (UB)</strong>, amb Màster en Pràctica Jurídica per l’<strong>Il·lustre Col·legi d’Advocats de Barcelona (ICAB)</strong>.",
    alex_bio_2: "Combina la direcció dels Departaments de <strong>Dret Mercantil i Societari</strong> amb el de <strong>Dret Laboral</strong> i Seguretat Social.",
    alex_honor: "Especialista en Assessorament Empresarial & Reestructuracions",
    anna_bio_1: "Llicenciada en Dret per la <strong>Universitat Autònoma de Barcelona (UAB)</strong>.",
    anna_bio_2: "Ha cursat el Postgrau de Pràctica Jurídica a l’<strong>Il·lustre Col·legi d’Advocats de Granollers (ICAVOR)</strong>.",
    anna_honor: "Especialista en Dret Immobiliari, Civil i Penal",
    values_kicker: "ELS NOSTRES PRINCIPIS",
    values_title: "Els Valors que Vertebren la Nostra Firma",
    values_subtitle: "El nostre compromís professional es basa en una conducta deontològica estricta i en la màxima dedicació a cada expedient.",
    val_1_t: "Professionalitat",
    val_1_d: "Rigurositat tècnica constant, actualització jurídica permanent i màxim estàndard d'exercici processal.",
    val_2_t: "Honestitat & Prudència",
    val_2_d: "Avaluació realista i honesta de les probabilitats d'èxit de cada assumpte sense generar falses expectatives.",
    val_3_t: "Confiança Mútua",
    val_3_d: "Construïm relacions duradores basades en la lleialtat, el secret professional i la comunicació fluida.",
    val_4_t: "Creativitat & Sentit Comú",
    val_4_d: "Solucions pràctiques i innovadores davant problemes complexos, sempre prioritzant la via més eficient per al client.",
    contact_kicker: "CONTACTE DIRECTE",
    contact_title_1: "Parlem del",
    contact_title_2: "teu cas legal.",
    contact_lead: "Visita'ns al nostre despatx al centre de Granollers o concerta una reunió presencial o telemàtica. Estarem encantats d'estudiar la teva situació amb total confidencialitat.",
    contact_addr_label: "Adreça",
    contact_map_link: "Veure mapa a Google Maps →",
    contact_tel_label: "Telèfon d'Atenció",
    contact_email_label: "Correu Electrònic",
    contact_hours: "Dilluns a Divendres: 9:00h - 14:00h / 16:00h - 19:30h",
    social_title: "Segueix-nos a xarxes socials:",
    form_heading: "Sol·licitar Cita o Consulta Legal",
    form_sub: "Omple el formulari i et respondrem en menys de 24 hores laborables.",
    form_lbl_name: "Nom complet *",
    form_lbl_email: "Correu electrònic *",
    form_lbl_phone: "Telèfon de contacte",
    form_lbl_area: "Àrea o assumpte de la consulta",
    opt_select: "-- Selecciona una especialitat --",
    opt_fam: "Dret Matrimonial i Família",
    opt_her: "Successions, Testaments i Herències",
    opt_pen: "Dret Penal i Defensa Judicial",
    opt_mer: "Mercantil, Societari & Compliance",
    opt_lab: "Laboral & Incapacitats",
    opt_imm: "Immobiliari, Arrendaments & Desnonaments",
    opt_con: "Concursos & Llei de Segona Oportunitat",
    opt_oth: "Altres assumptes jurídics",
    form_lbl_msg: "Missatge o breu explicació del cas *",
    form_consent: "He llegit i accepto la política de privacitat i el tractament de les meves dades exclusivament per a gestionar aquesta consulta jurídica.",
    form_btn_submit: "Enviar Consulta Confidencial",
    map_open: "Obrir a Google Maps",
    footer_bio: "Firma d'advocats i d'assessorament legal integral al centre de Granollers. Compromís amb el rigor, l'ètica i la qualitat jurídica al servei dels nostres clients.",
    f_links_title: "Navegació",
    f_spec_title: "Especialitats",
    f_contact_title: "Contacte",
    f_rights: "Tots els drets reservats.",
    f_privacy: "Política de Privacitat",
    f_legal: "Avís Legal",
    f_cookies: "Cookies"
  },
  es: {
    top_address: "C/ Barcelona, 7 - 1º, Granollers",
    nav_presentation: "Presentación",
    nav_specialties: "Especialidades",
    nav_team: "El Equipo",
    nav_values: "Filosofía",
    nav_contact: "Contacto",
    nav_cta: "Solicitar Cita",
    hero_badge: "Firma Legal en Granollers & Barcelona",
    hero_title_1: "Rigor, compromiso",
    hero_title_2: "y excelencia jurídica",
    hero_title_3: "en el centro de Granollers.",
    hero_desc: "ARS Advocats i Assessors es un despacho moderno, joven y ágil integrado por abogados de primer nivel. Aportamos soluciones prácticas, sentido común y una visión estratégica global para proteger los intereses de particulares y empresas.",
    hero_cta_consult: "Solicitar Primera Consulta",
    hero_cta_specialties: "Explorar Áreas de Derecho",
    hero_btn_explore: "Explorar Áreas de Derecho",
    stat_areas: "Áreas de especialización jurídica",
    stat_board: "Miembros Junta de Gobierno & ICAB",
    stat_dedication: "Compromiso ético y atención personalizada",
    float_title: "Ubicación Estratégica",
    float_sub: "Calle de Barcelona, 7 · Granollers",
    float_desc: "Atención directa con el socio responsable de tu caso.",
    badge_firm: "Firma de Abogados Integral",
    badge_bw_to_color: "Clica para ver en color",
    badge_color_to_bw: "Color activo · Clica para B/N",
    pres_kicker: "PRESENTACIÓN INSTITUCIONAL",
    pres_title_1: "Un despacho joven,",
    pres_title_2: "moderno, ágil y comprometido.",
    pres_p1: "ARS Advocats i Assessors somos una firma de abogados y de asesoramiento legal integral, situada en el centro histórico y comercial de Granollers.",
    pres_p2: "El nuestro es un despacho joven, moderno y ágil, integrado por profesionales altamente comprometidos y abogados de primer nivel. Aportamos una amplia experiencia en todas las áreas de especialización a las que nos dedicamos, con una visión global que prioriza el servicio, el rigor, la calidad y el compromiso firme con el cliente.",
    pres_p3: "Trabajamos con pasión, apostando constantemente por la mejora y la innovación. Creemos firmemente en el sentido común y en la aplicación de soluciones prácticas y creativas que resuelvan eficazmente los problemas e inquietudes legales, haciendo nuestros sus retos.",
    pres_quote: "Para garantizar un asesoramiento eficaz y de calidad, consideramos imprescindible conocer en profundidad a nuestros clientes, así como sus negocios y circunstancias particulares.",
    pres_motto: "El objetivo principal de ARS se resume en una palabra: CALIDAD.",
    feat_1_title: "Sentido Común & Creatividad",
    feat_1_desc: "Evitamos soluciones estándar; diseñamos estrategias a medida para cada conflicto.",
    feat_2_title: "Trato Directo con Socios",
    feat_2_desc: "Comunicación transparente, inmediata y sin intermediarios innecesarios.",
    spec_kicker: "ÁREAS DE PRÁCTICA JURÍDICA",
    spec_title: "Servicio Integral en Derecho Privado y Público",
    spec_subtitle: "Nos dedicamos a atender y resolver de forma eficaz, coherente y ética cualquier conflicto o necesidad legal planteada por particulares, familias y sociedades mercantiles.",
    filter_all: "Todas las Áreas",
    filter_civil: "Civil & Familia",
    filter_business: "Mercantil & Empresa",
    filter_criminal: "Penal",
    filter_labor: "Laboral & Daños",
    filter_property: "Inmobiliario & Financiero",
    sp_1_title: "Derecho Matrimonial y de Familia",
    sp_1_desc: "Procesos de separación y divorcio (mutuo acuerdo o contencioso), redacción de convenios reguladores, guardia y custodia, pensión de alimentos y modificación de medidas judiciales.",
    sp_2_title: "Sucesiones, Testamentos y Herencias",
    sp_2_desc: "Planificación sucesoria patrimonial, tramitación y aceptación de herencias ante notario, declaraciones de herederos, reclamación de legítima e impugnación de testamentos.",
    sp_3_title: "Desahucios y Arrendamientos",
    sp_3_desc: "Recuperación rápida de la posesión de inmuebles por impago de rentas o expiración de plazo. Redacción de contratos de arrendamiento de vivienda y local comercial.",
    sp_4_title: "Obligaciones y Contratos",
    sp_4_desc: "Redacción, interpretación y negociación de contratos civiles y mercantiles. Resolución por incumplimiento, reclamación de vicios ocultos e indemnización de daños y perjuicios.",
    sp_5_title: "Reclamaciones de Cantidad",
    sp_5_desc: "Reclamación extrajudicial y judicial de impagos y deudas pendientes. Procedimientos monitorios, ordinarios, verbales y ejecución de activos y embargos patrimoniales.",
    sp_6_title: "Comunidades de Propietarios",
    sp_6_desc: "Asesoramiento en Propiedad Horizontal, impugnación de acuerdos comunitarios nulos o perjudiciales, reclamación a morosos y responsabilidad por defectos constructivos.",
    sp_7_title: "Derecho Bancario & Cláusulas Abusivas",
    sp_7_desc: "Defensa frente a abusos bancarios: cláusula suelo, gastos de formalización de hipoteca, comisiones indebidas, tarjetas revolving y ejecuciones hipotecarias.",
    sp_8_title: "Derecho Penal & Defensa Judicial",
    sp_8_desc: "Asistencia urgente al detenido en comisaría y juzgado de guardia. Defensa y acusación particular en procedimientos por delitos leves, menos graves y graves.",
    sp_9_title: "Violencia de Género",
    sp_9_desc: "Atención especializada, urgente y sensible. Solicitud de órdenes de protección y alejamiento, medidas cautelares personales y patrimoniales, y acompañamiento integral.",
    sp_10_title: "Derecho Económico & Compliance",
    sp_10_desc: "Prevención de delitos corporativos (Corporate Compliance), responsabilidad penal de la persona jurídica, estafas, apropiaciones indebidas y delitos societarios.",
    sp_11_title: "Accidentes de Tráfico",
    sp_11_desc: "Defensa de los derechos de las víctimas de accidentes de circulación. Cálculo exacto de baremos médico-legales y máxima indemnización por daños materiales, físicos y secuelas.",
    sp_12_title: "Derecho Laboral & Seguridad Social",
    sp_12_desc: "Despidos disciplinarios y objetivos, reclamación de salarios, sanciones laborales, expedientes de regulación de empleo (ERE/ERTE) y conciliación previa (CMAC).",
    sp_13_title: "Procedimientos de Incapacidad Laboral",
    sp_13_desc: "Tramitación y reclamación judicial de pensiones por incapacidad laboral permanente (parcial, total, absoluta y gran invalidez). Impugnación de altas médicas del INSS y mutuas.",
    sp_14_title: "Asesoramiento a Sociedades Mercantiles",
    sp_14_desc: "Constitución de empresas, redacción de pactos de socios, acuerdos de confidencialidad, fusiones, aumentos de capital, secretaría de consejos y conflictos entre socios.",
    sp_15_title: "Concursos & Ley de Segunda Oportunidad",
    sp_15_desc: "Reestructuración de deudas e insolvencias para pymes y autónomos. Aplicación de la Ley de la Segunda Oportunidad para la cancelación definitiva de deudas personales.",
    spec_cta_lead: "¿Necesitas asesoramiento en otra materia o tienes dudas sobre la viabilidad de tu caso?",
    spec_cta_btn: "Consúltanos sin compromiso",
    team_kicker: "PROFESIONALES DE PRIMER NIVEL",
    team_title: "El Equipo de ARS Advocats",
    team_subtitle: "Un equipo directivo cohesionado, comprometido y accesible, con sólida formación en la Universidad de Barcelona y presencia activa en las instituciones colegiales.",
    team_role_partner: "Socio Director",
    team_role_collab: "Abogada Colaboradora",
    roger_bio_1: "Licenciado en Derecho por la <strong>Universitat de Barcelona (UB)</strong>, con Máster en Abogacía por el <strong>Ilustre Colegio de Abogados de Barcelona (ICAB)</strong>.",
    roger_bio_2: "Se encarga y responsabiliza de la dirección de los Departamentos de <strong>Derecho Civil</strong>, <strong>Derecho de Familia</strong> y <strong>Derecho Penal</strong>.",
    roger_honor: "Miembro de la Junta de Gobierno del ICAVOR (Granollers)",
    team_btn_contact: "Contactar",
    alex_bio_1: "Licenciado en Derecho por la <strong>Universitat de Barcelona (UB)</strong>, con Máster en Práctica Jurídica por el <strong>Ilustre Colegio de Abogados de Barcelona (ICAB)</strong>.",
    alex_bio_2: "Combina la dirección de los Departamentos de <strong>Derecho Mercantil y Societario</strong> con el de <strong>Derecho Laboral</strong> y Seguridad Social.",
    alex_honor: "Especialista en Asesoramiento Empresarial & Reestructuraciones",
    anna_bio_1: "Licenciada en Derecho por la <strong>Universitat Autònoma de Barcelona (UAB)</strong>.",
    anna_bio_2: "Ha cursado el Posgrado de Práctica Jurídica en el <strong>Ilustre Colegio de Abogados de Granollers (ICAVOR)</strong>.",
    anna_honor: "Especialista en Derecho Inmobiliario, Civil y Penal",
    values_kicker: "NUESTROS PRINCIPIOS",
    values_title: "Los Valores que Vertebran Nuestra Firma",
    values_subtitle: "Nuestro compromiso profesional se basa en una conducta deontológica estricta y en la máxima dedicación a cada expediente.",
    val_1_t: "Profesionalidad",
    val_1_d: "Rigurosidad técnica constante, actualización jurídica permanente y máximo estándar de ejercicio procesal.",
    val_2_t: "Honestidad & Prudencia",
    val_2_d: "Evaluación realista y honesta de las probabilidades de éxito de cada asunto sin generar falsas expectativas.",
    val_3_t: "Confianza Mutua",
    val_3_d: "Construimos relaciones duraderas basadas en la lealtad, el secreto profesional y la comunicación fluida.",
    val_4_t: "Creatividad & Sentido Común",
    val_4_d: "Soluciones prácticas e innovadoras ante problemas complejos, siempre priorizando la vía más eficiente para el cliente.",
    contact_kicker: "CONTACTO DIRECTO",
    contact_title_1: "Hablemos de",
    contact_title_2: "tu caso legal.",
    contact_lead: "Visítanos en nuestro despacho en el centro de Granollers o concierta una reunión presencial o telemática. Estaremos encantados de estudiar tu situación con total confidencialidad.",
    contact_addr_label: "Dirección",
    contact_map_link: "Ver mapa en Google Maps →",
    contact_tel_label: "Teléfono de Atención",
    contact_email_label: "Correo Electrónico",
    contact_hours: "Lunes a Viernes: 9:00h - 14:00h / 16:00h - 19:30h",
    social_title: "Síguenos en redes sociales:",
    form_heading: "Solicitar Cita o Consulta Legal",
    form_sub: "Rellena el formulario y te responderemos en menos de 24 horas laborables.",
    form_lbl_name: "Nombre completo *",
    form_lbl_email: "Correo electrónico *",
    form_lbl_phone: "Teléfono de contacto",
    form_lbl_area: "Área o asunto de la consulta",
    opt_select: "-- Selecciona una especialidad --",
    opt_fam: "Derecho Matrimonial y Familia",
    opt_her: "Sucesiones, Testamentos y Herencias",
    opt_pen: "Derecho Penal y Defensa Judicial",
    opt_mer: "Mercantil, Societario & Compliance",
    opt_lab: "Laboral & Incapacidades",
    opt_imm: "Inmobiliario, Arrendamientos & Desahucios",
    opt_con: "Concursos & Ley de Segunda Oportunidad",
    opt_oth: "Otros asuntos jurídicos",
    form_lbl_msg: "Mensaje o breve explicación del caso *",
    form_consent: "He leído y acepto la política de privacidad y el tratamiento de mis datos exclusivamente para gestionar esta consulta jurídica.",
    form_btn_submit: "Enviar Consulta Confidencial",
    map_open: "Abrir en Google Maps",
    footer_bio: "Firma de abogados y de asesoramiento legal integral en el centro de Granollers. Compromiso con el rigor, la ética y la calidad jurídica al servicio de nuestros clientes.",
    f_links_title: "Navegación",
    f_spec_title: "Especialidades",
    f_contact_title: "Contacto",
    f_rights: "Todos los derechos reservados.",
    f_privacy: "Política de Privacidad",
    f_legal: "Aviso Legal",
    f_cookies: "Cookies"
  },
  en: {
    top_address: "C/ Barcelona, 7 - 1st Floor, Granollers",
    nav_presentation: "Overview",
    nav_specialties: "Practice Areas",
    nav_team: "Our Team",
    nav_values: "Philosophy",
    nav_contact: "Contact",
    nav_cta: "Book Consultation",
    hero_badge: "Law Firm in Granollers & Barcelona",
    hero_title_1: "Rigor, commitment",
    hero_title_2: "and legal excellence",
    hero_title_3: "in downtown Granollers.",
    hero_desc: "ARS Advocats i Assessors is a modern, dynamic, and agile law firm formed by top-tier attorneys. We provide pragmatic solutions, common sense, and comprehensive strategic foresight to safeguard the interests of individuals and corporations.",
    hero_cta_consult: "Request Initial Consultation",
    hero_cta_specialties: "Explore Practice Areas",
    hero_btn_explore: "Explore Practice Areas",
    stat_areas: "Specialized practice areas",
    stat_board: "Governing Board Members & ICAB",
    stat_dedication: "Ethical commitment & bespoke attention",
    float_title: "Prime Location",
    float_sub: "Carrer de Barcelona, 7 · Granollers",
    float_desc: "Direct communication with the lead partner handling your case.",
    badge_firm: "Comprehensive Law Firm",
    badge_bw_to_color: "Click to view full color",
    badge_color_to_bw: "Color active · Click for B/W",
    pres_kicker: "INSTITUTIONAL PRESENTATION",
    pres_title_1: "A youthful, modern,",
    pres_title_2: "agile and dedicated firm.",
    pres_p1: "ARS Advocats i Assessors is a comprehensive law and legal advisory firm located in the historic and commercial heart of Granollers.",
    pres_p2: "Our office is modern, agile, and energetic, comprised of deeply committed professionals and top-tier attorneys. We contribute extensive experience across all our specialized practice areas, with a global vision that prioritizes client care, rigor, technical quality, and unyielding dedication.",
    pres_p3: "We work with passion, constantly pursuing innovation and continuous improvement. We firmly believe in common sense and in implementing pragmatic, creative solutions that effectively resolve legal challenges, making our clients' goals our own.",
    pres_quote: "To ensure effective, premium legal counsel, we consider it paramount to understand our clients in depth, along with their businesses and individual circumstances.",
    pres_motto: "The core mission of ARS is defined in one word: QUALITY.",
    feat_1_title: "Common Sense & Creativity",
    feat_1_desc: "We avoid boilerplate formulas; we craft bespoke legal strategies tailored to each matter.",
    feat_2_title: "Direct Partner Contact",
    feat_2_desc: "Transparent, immediate communication without unnecessary intermediaries.",
    spec_kicker: "AREAS OF LEGAL PRACTICE",
    spec_title: "Comprehensive Counsel in Private & Public Law",
    spec_subtitle: "We are devoted to efficiently, coherently, and ethically resolving any legal conflict or objective presented by individuals, families, and corporate enterprises.",
    filter_all: "All Practice Areas",
    filter_civil: "Civil & Family",
    filter_business: "Corporate & Business",
    filter_criminal: "Criminal Law",
    filter_labor: "Labor & Claims",
    filter_property: "Real Estate & Finance",
    sp_1_title: "Family & Matrimonial Law",
    sp_1_desc: "Separation and divorce proceedings (consensual or contentious), regulatory marital agreements, child custody, alimony, and modification of judicial decrees.",
    sp_2_title: "Estates, Wills & Inheritances",
    sp_2_desc: "Estate tax and succession planning, probate procedures before notaries, declarations of heirs, statutory share claims, and will challenges.",
    sp_3_title: "Evictions & Tenancy Law",
    sp_3_desc: "Swift property repossession for non-payment of rent or lease termination. Drafting residential and commercial lease agreements.",
    sp_4_title: "Contracts & Obligations",
    sp_4_desc: "Drafting, reviewing, and negotiating civil and commercial agreements. Breach of contract litigation, hidden defect claims, and damages recovery.",
    sp_5_title: "Debt Collection & Recovery",
    sp_5_desc: "Extrajudicial and judicial collection of unpaid debts. Summary payment proceedings, ordinary lawsuits, asset discovery, and enforcement of attachments.",
    sp_6_title: "Homeowners' Associations",
    sp_6_desc: "Counsel on Horizontal Property regulations, challenges to null community resolutions, delinquent fee recovery, and building defect liability.",
    sp_7_title: "Banking Law & Abusive Clauses",
    sp_7_desc: "Defense against financial malpractice: mortgage floor clauses, loan arrangement expenses, unfair bank fees, revolving credit cards, and foreclosures.",
    sp_8_title: "Criminal Law & Defense",
    sp_8_desc: "Urgent detainee assistance at police precincts and on-duty courts. Defense and private prosecution in misdemeanors, intermediate, and major felony offenses.",
    sp_9_title: "Gender & Domestic Violence",
    sp_9_desc: "Specialized, sensitive, and immediate legal assistance. Petitions for protective and restraining orders, preliminary personal and property relief.",
    sp_10_title: "White-Collar Crime & Compliance",
    sp_10_desc: "Corporate criminal prevention and compliance programs, corporate criminal liability, fraud, embezzlement, and director liability litigation.",
    sp_11_title: "Traffic & Personal Injury",
    sp_11_desc: "Vigorous defense of accident victims' rights. Precise actuarial and medical assessment under Spanish legal scales for maximum compensation.",
    sp_12_title: "Labor Law & Social Security",
    sp_12_desc: "Objective and disciplinary dismissals, unpaid wage litigation, disciplinary sanctions, collective redundancies (ERE/ERTE), and labor conciliation (CMAC).",
    sp_13_title: "Disability & Pension Claims",
    sp_13_desc: "Judicial appeals and proceedings for permanent disability pensions (partial, total, absolute, and severe). Contesting medical discharges from social security.",
    sp_14_title: "Corporate & Commercial Law",
    sp_14_desc: "Company formation, shareholder agreements, non-disclosure agreements, mergers, capital increases, board secretarial duties, and shareholder dispute resolution.",
    sp_15_title: "Insolvency & Second Chance Law",
    sp_15_desc: "Debt restructuring and bankruptcy proceedings for SMEs and entrepreneurs. Legal discharge of personal debt under Spain's Second Chance Law.",
    spec_cta_lead: "Do you require counsel in another legal field or have questions about the merits of your case?",
    spec_cta_btn: "Inquire Without Obligation",
    team_kicker: "FIRST-CLASS PROFESSIONALS",
    team_title: "The ARS Advocats Team",
    team_subtitle: "A unified, accessible, and dedicated leadership team with advanced degrees from the University of Barcelona and active participation in bar associations.",
    team_role_partner: "Managing Partner",
    team_role_collab: "Associate Attorney",
    roger_bio_1: "Law Degree from the <strong>University of Barcelona (UB)</strong>, with a Master's in Legal Practice from the <strong>Barcelona Bar Association (ICAB)</strong>.",
    roger_bio_2: "Leads and oversees the departments of <strong>Civil Law</strong>, <strong>Family Law</strong>, and <strong>Criminal Law</strong>.",
    roger_honor: "Governing Board Member of the Granollers Bar Association (ICAVOR)",
    team_btn_contact: "Contact",
    alex_bio_1: "Law Degree from the <strong>University of Barcelona (UB)</strong>, with a Master's in Legal Practice from the <strong>Barcelona Bar Association (ICAB)</strong>.",
    alex_bio_2: "Heads both the <strong>Commercial & Corporate Law</strong> Department and the <strong>Labor & Social Security Law</strong> Department.",
    alex_honor: "Specialist in Corporate Restructuring & Business Advisory",
    anna_bio_1: "Law Degree from the <strong>Autonomous University of Barcelona (UAB)</strong>.",
    anna_bio_2: "Postgraduate Diploma in Legal Practice from the <strong>Granollers Bar Association (ICAVOR)</strong>.",
    anna_honor: "Specialist in Real Estate, Civil, and Criminal Law",
    values_kicker: "OUR CORE PRINCIPLES",
    values_title: "The Values Anchoring Our Practice",
    values_subtitle: "Our professional pledge is built upon stringent ethical standards and complete dedication to each entrusted case.",
    val_1_t: "Professionalism",
    val_1_d: "Continuous technical rigor, permanent jurisprudential updating, and the highest standards of procedural advocacy.",
    val_2_t: "Integrity & Prudence",
    val_2_d: "Realistic, candid appraisal of legal prospects without cultivating unwarranted expectations.",
    val_3_t: "Mutual Trust",
    val_3_d: "We cultivate enduring relationships rooted in loyalty, professional secrecy, and fluid transparency.",
    val_4_t: "Creativity & Common Sense",
    val_4_d: "Pragmatic, forward-thinking solutions for intricate dilemmas, always pursuing the most cost-effective path for the client.",
    contact_kicker: "DIRECT CONTACT",
    contact_title_1: "Let's discuss",
    contact_title_2: "your legal matter.",
    contact_lead: "Visit our Granollers downtown office or arrange an in-person or videoconference consultation. We will gladly analyze your situation under strict confidentiality.",
    contact_addr_label: "Address",
    contact_map_link: "Open in Google Maps →",
    contact_tel_label: "Direct Phone Line",
    contact_email_label: "Email Address",
    contact_hours: "Monday to Friday: 9:00 AM - 2:00 PM / 4:00 PM - 7:30 PM",
    social_title: "Follow us on social networks:",
    form_heading: "Request Consultation or Appointment",
    form_sub: "Complete the form below and an attorney will respond within 24 business hours.",
    form_lbl_name: "Full Name *",
    form_lbl_email: "Email Address *",
    form_lbl_phone: "Contact Phone Number",
    form_lbl_area: "Legal Practice Area",
    opt_select: "-- Select a practice area --",
    opt_fam: "Family & Matrimonial Law",
    opt_her: "Estates, Wills & Inheritances",
    opt_pen: "Criminal Defense & Litigation",
    opt_mer: "Corporate, Commercial & Compliance",
    opt_lab: "Labor & Disability Law",
    opt_imm: "Real Estate, Leases & Evictions",
    opt_con: "Insolvency & Second Chance Law",
    opt_oth: "Other legal matters",
    form_lbl_msg: "Case summary or message *",
    form_consent: "I have read and accept the privacy policy and consent to the processing of my data exclusively to address this legal inquiry.",
    form_btn_submit: "Send Confidential Inquiry",
    map_open: "Open in Google Maps",
    footer_bio: "Comprehensive law firm and legal counsel based in downtown Granollers. Committed to technical rigor, ethics, and legal excellence serving private and corporate clients.",
    f_links_title: "Navigation",
    f_spec_title: "Practice Areas",
    f_contact_title: "Contact",
    f_rights: "All rights reserved.",
    f_privacy: "Privacy Policy",
    f_legal: "Legal Notice",
    f_cookies: "Cookies Policy"
  }
};

const legalContents = {
  ca: {
    privacyTitle: "Política de Privacitat",
    privacyHtml: `
      <h4>Responsable del Tractament</h4>
      <p>ARS Advocats i Assessors, amb domicili a Carrer de Barcelona, 7 - 1r, 08401 Granollers (Barcelona). Correu de contacte: info@arsadvocats.com.</p>
      <h4>Finalitat del Tractament</h4>
      <p>Les dades facilitades mitjançant els formularis de contacte, trucades o correus electrònics seran tractades exclusivament per a gestionar la sol·licitud de consulta o atenció jurídica sol·licitada.</p>
      <h4>Legitimació i Conservació</h4>
      <p>La base legal és el consentiment exprés de l'usuari i la relació precontractual/contractual d'assessorament jurídic. Les dades es conservaran mentre duri la gestió de la consulta o els terminis legals d'exigència de responsabilitats deontològiques i civils.</p>
      <h4>Drets de l'Usuari</h4>
      <p>Pots exercir els teus drets d'accés, rectificació, supressió, limitació i oposició adreçant una comunicació escrita a info@arsadvocats.com aportant còpia del document d'identitat.</p>
    `,
    legalTitle: "Avís Legal i Règim Col·legial",
    legalHtml: `
      <h4>Informació General</h4>
      <p>En compliment de la Llei 34/2002 de Serveis de la Societat de la Informació (LSSI-CE), s'informa que aquest lloc web és titularitat d'ARS Advocats i Assessors, establerts a Granollers (Barcelona).</p>
      <h4>Normativa Professional</h4>
      <p>Els socis i lletrats que integren la firma estan col·legiats a l'Il·lustre Col·legi d'Advocats de Granollers (ICAVOR) i a l'Il·lustre Col·legi d'Advocats de Barcelona (ICAB), sotmesos a l'Estatut General de l'Advocacia Espanyola i al Codi Deontològic de la professió.</p>
      <h4>Propietat Intel·lectual</h4>
      <p>Tots els continguts, dissenys, textos i logotips d'aquest lloc web pertanyen als seus respectius titulars legítims.</p>
    `,
    cookiesTitle: "Política de Cookies",
    cookiesHtml: `
      <p>Aquest lloc web utilitza exclusivament cookies tècniques indispensables per al correcte funcionament de la navegació, la memorització de l'idioma seleccionat i la seguretat del lloc. No s'utilitzen cookies de seguiment comercial de tercers sense el teu consentiment explícit.</p>
    `
  },
  es: {
    privacyTitle: "Política de Privacidad",
    privacyHtml: `
      <h4>Responsable del Tratamiento</h4>
      <p>ARS Advocats i Assessors, con domicilio en Calle de Barcelona, 7 - 1º, 08401 Granollers (Barcelona). Correo de contacto: info@arsadvocats.com.</p>
      <h4>Finalidad del Tratamiento</h4>
      <p>Los datos facilitados a través de formularios, llamadas o correos se tratarán exclusivamente para gestionar la solicitud de consulta o encargo jurídico solicitado.</p>
      <h4>Legitimación y Conservación</h4>
      <p>La base legal es el consentimiento expreso del usuario y la relación precontractual o contractual de asesoramiento legal. Los datos se conservarán durante el tiempo necesario para la atención del asunto y los plazos legales aplicables.</p>
      <h4>Derechos del Usuario</h4>
      <p>Puedes ejercer tus derechos de acceso, rectificación, supresión, limitación y oposición dirigiendo un escrito a info@arsadvocats.com junto a copia de documento de identidad.</p>
    `,
    legalTitle: "Aviso Legal y Régimen Colegial",
    legalHtml: `
      <h4>Información General</h4>
      <p>En cumplimiento de la Ley 34/2002 de Servicios de la Sociedad de la Información (LSSI-CE), se informa de que este sitio web es titularidad de ARS Advocats i Assessors, radicados en Granollers (Barcelona).</p>
      <h4>Normativa Profesional</h4>
      <p>Los letrados de la firma están debidamente colegiados en el Ilustre Colegio de Abogados de Granollers (ICAVOR) y en el Ilustre Colegio de Abogados de Barcelona (ICAB), sujetos al Estatuto General de la Abogacía y al Código Deontológico.</p>
      <h4>Propiedad Intelectual</h4>
      <p>Todos los contenidos, diseños, textos y logotipos de este sitio pertenecen a sus legítimos titulares.</p>
    `,
    cookiesTitle: "Política de Cookies",
    cookiesHtml: `
      <p>Este sitio web utiliza exclusivamente cookies técnicas esenciales para garantizar la navegación correcta, almacenar la preferencia de idioma y la seguridad. No se emplean cookies de rastreo comercial publicitario de terceros.</p>
    `
  },
  en: {
    privacyTitle: "Privacy Policy",
    privacyHtml: `
      <h4>Data Controller</h4>
      <p>ARS Advocats i Assessors, located at Carrer de Barcelona, 7 - 1st Floor, 08401 Granollers (Barcelona, Spain). Contact email: info@arsadvocats.com.</p>
      <h4>Purpose of Data Processing</h4>
      <p>Personal data collected via inquiry forms, phone calls, or emails will be processed strictly to manage and respond to legal consultation requests.</p>
      <h4>Lawful Basis & Retention</h4>
      <p>The processing is legitimized by express user consent and pre-contractual legal advisory relationships. Data will be retained throughout the case management and during statutory limitation periods.</p>
      <h4>User Rights</h4>
      <p>You may exercise rights of access, rectification, erasure, restriction, and opposition by sending a written notice along with proof of identity to info@arsadvocats.com.</p>
    `,
    legalTitle: "Legal Notice & Regulatory Standing",
    legalHtml: `
      <h4>General Information</h4>
      <p>Pursuant to Spanish Law 34/2002 (LSSI-CE), notice is hereby given that this website is the property of ARS Advocats i Assessors, based in Granollers (Barcelona, Spain).</p>
      <h4>Professional Regulation</h4>
      <p>Firm attorneys are officially registered with the Bar Association of Granollers (ICAVOR) and the Bar Association of Barcelona (ICAB), governed by the Spanish General Advocacy Statute and Code of Conduct.</p>
      <h4>Intellectual Property</h4>
      <p>All contents, branding, texts, and imagery are protected under intellectual property legislation and remain the exclusive property of their respective owners.</p>
    `,
    cookiesTitle: "Cookies Policy",
    cookiesHtml: `
      <p>This website uses only essential technical cookies necessary for safe navigation, language preferences, and basic functionality. No commercial third-party advertising trackers are used.</p>
    `
  }
};

document.addEventListener('DOMContentLoaded', () => {
  // Set Current Year in footer
  const yearEl = document.getElementById('year');
  if (yearEl) yearEl.textContent = new Date().getFullYear();

  // Language management
  let currentLang = localStorage.getItem('ars_lang') || 'ca';

  function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('ars_lang', lang);
    document.body.setAttribute('data-lang', lang);
    document.documentElement.setAttribute('lang', lang);

    // Update buttons state
    document.querySelectorAll('.lang-btn').forEach(btn => {
      if (btn.getAttribute('data-switch-lang') === lang) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Translate elements with data-i18n
    const dict = translations[lang] || translations.ca;
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key] !== undefined) {
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
          el.placeholder = dict[key];
        } else {
          el.innerHTML = dict[key];
        }
      }
    });
  }

  // Language buttons click
  document.querySelectorAll('[data-switch-lang]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const targetLang = btn.getAttribute('data-switch-lang');
      applyLanguage(targetLang);
    });
  });

  // Initial apply
  applyLanguage(currentLang);

  // Mobile menu drawer
  const mobileToggle = document.getElementById('mobileToggle');
  const mobileMenu = document.getElementById('mobileMenu');

  if (mobileToggle && mobileMenu) {
    mobileToggle.addEventListener('click', () => {
      const isOpen = mobileMenu.classList.contains('open');
      if (isOpen) {
        mobileMenu.classList.remove('open');
        mobileToggle.setAttribute('aria-expanded', 'false');
      } else {
        mobileMenu.classList.add('open');
        mobileToggle.setAttribute('aria-expanded', 'true');
      }
    });

    // Close when clicking mobile links
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.remove('open');
        mobileToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Practice area category filter
  const filterPills = document.querySelectorAll('.filter-pills .pill');
  const specCards = document.querySelectorAll('.specialties-grid .spec-card');

  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');

      const filterVal = pill.getAttribute('data-filter');

      specCards.forEach(card => {
        const cat = card.getAttribute('data-category');
        if (filterVal === 'all' || cat === filterVal) {
          card.style.display = 'flex';
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, 30);
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // Scroll Reveal Animations
  const reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    reveals.forEach(el => observer.observe(el));
  } else {
    reveals.forEach(el => el.classList.add('active'));
  }

  // Modals for Legal Information
  const modal = document.getElementById('legalModal');
  const modalBackdrop = document.getElementById('modalBackdrop');
  const modalClose = document.getElementById('modalClose');
  const modalTitle = document.getElementById('modalTitle');
  const modalBody = document.getElementById('modalBody');

  function openModal(title, html) {
    if (!modal) return;
    modalTitle.textContent = title;
    modalBody.innerHTML = html;
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    if (!modal) return;
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  if (modalBackdrop) modalBackdrop.addEventListener('click', closeModal);
  if (modalClose) modalClose.addEventListener('click', closeModal);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });

  document.getElementById('openPrivacyModal')?.addEventListener('click', (e) => {
    e.preventDefault();
    const texts = legalContents[currentLang] || legalContents.ca;
    openModal(texts.privacyTitle, texts.privacyHtml);
  });

  document.getElementById('openLegalModal')?.addEventListener('click', (e) => {
    e.preventDefault();
    const texts = legalContents[currentLang] || legalContents.ca;
    openModal(texts.legalTitle, texts.legalHtml);
  });

  document.getElementById('openCookiesModal')?.addEventListener('click', (e) => {
    e.preventDefault();
    const texts = legalContents[currentLang] || legalContents.ca;
    openModal(texts.cookiesTitle, texts.cookiesHtml);
  });

  // Contact form submission
  const contactForm = document.getElementById('contactForm');
  const formFeedback = document.getElementById('formFeedback');
  const submitBtn = document.getElementById('submitBtn');

  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const name = document.getElementById('formName').value.trim();
      const email = document.getElementById('formEmail').value.trim();
      const message = document.getElementById('formMessage').value.trim();
      const consent = document.getElementById('formConsent').checked;

      if (!name || !email || !message || !consent) {
        formFeedback.style.display = 'block';
        formFeedback.className = 'form-feedback error';
        formFeedback.textContent = currentLang === 'ca'
          ? "Si us plau, omple tots els camps obligatoris (*) i accepta la política de privacitat."
          : "Por favor, completa todos los campos obligatorios (*) y acepta la política de privacidad.";
        return;
      }

      // Email basic format check
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        formFeedback.style.display = 'block';
        formFeedback.className = 'form-feedback error';
        formFeedback.textContent = currentLang === 'ca'
          ? "Si us plau, introdueix una adreça de correu electrònic vàlida."
          : "Por favor, introduce una dirección de correo electrónico válida.";
        return;
      }

      // Loading state
      submitBtn.disabled = true;
      submitBtn.style.opacity = '0.7';
      const originalText = submitBtn.innerHTML;
      submitBtn.innerHTML = currentLang === 'ca' ? "Enviant consulta..." : "Enviando consulta...";

      setTimeout(() => {
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
        submitBtn.innerHTML = originalText;
        contactForm.reset();

        formFeedback.style.display = 'block';
        formFeedback.className = 'form-feedback success';
        if (currentLang === 'en') {
          formFeedback.textContent = `Thank you, ${name}. We have successfully received your inquiry. A specialist attorney will contact you shortly.`;
        } else if (currentLang === 'es') {
          formFeedback.textContent = `Gracias, ${name}. Hemos recibido tu consulta correctamente. Un abogado del departamento correspondiente se pondrá en contacto contigo en breve.`;
        } else {
          formFeedback.textContent = `Gràcies, ${name}. Hem rebut la teva consulta correctament. Un advocat del departament corresponent es posarà en contacte amb tu en breu.`;
        }
      }, 700);
    });
  }

  // 3D Tilt interaction on Hero Emblem Stage (responsive from anywhere on the web)
  const emblemStage = document.getElementById('heroEmblemStage');
  if (emblemStage && window.matchMedia('(pointer: fine)').matches) {
    let ticking = false;

    window.addEventListener('mousemove', (e) => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const rect = emblemStage.getBoundingClientRect();
          // Check if hero emblem is within or near the viewport
          if (rect.bottom > -100 && rect.top < window.innerHeight + 100) {
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;

            const deltaX = (e.clientX - centerX) / (window.innerWidth / 2);
            const deltaY = (e.clientY - centerY) / (window.innerHeight / 2);

            const rotateX = Math.max(-12, Math.min(12, deltaY * -10));
            const rotateY = Math.max(-12, Math.min(12, deltaX * 10));

            emblemStage.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg)`;
          }
          ticking = false;
        });
        ticking = true;
      }
    });

    document.addEventListener('mouseleave', () => {
      emblemStage.style.transition = 'transform 0.8s cubic-bezier(0.16, 1, 0.3, 1)';
      emblemStage.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg)';
      setTimeout(() => {
        emblemStage.style.transition = '';
      }, 800);
    });
  }

  // Interactive presentation photo color toggle (B/N <-> Color on click)
  const photoCard = document.getElementById('presentationPhotoCard');
  if (photoCard) {
    photoCard.addEventListener('click', () => {
      photoCard.classList.toggle('is-colored');
    });

    photoCard.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        photoCard.classList.toggle('is-colored');
      }
    });
  }
});
