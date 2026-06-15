// Global state
let currentBrowser = "brave";
let isBrowserConnected = false;
let chatHistory = [];
let selectedFiles = [];
let currentSessionId = Date.now().toString();
let activeMode = "instant"; // "instant" or "expert"
let activeInstantAssistant = "chatgpt"; // "chatgpt", "gemini", or "deepseek"

const translations = {
    ar: {
        pageTitle: "AI Spark | المنسق الذكي",
        subTitle: "المنسق المحلي الذكي",
        braveBrowser: "متصفح Brave",
        syncBtn: "المزامنة",
        refreshBtn: "تحديث",
        historyBtn: "السجل",
        newChatBtn: "محادثة جديدة",
        today: "اليوم",
        yesterday: "أمس",
        previous7: "آخر 7 أيام",
        older: "أقدم",
        dashboardTitle: "لوحة التحكم بالبث الموزع",
        dashboardDesc: "اكتب سؤالك وسيقوم النظام ببثه بالتزامن إلى ChatGPT و Gemini و DeepSeek، ثم تجميعه وتلخيصه محلياً عبر Claude.",
        promptPlaceholder: "اكتب سؤالك هنا بالتفصيل... (مثال: اشرح لي مفهوم الحوسبة السحابية وما هي أنواعها؟)",
        claudeSynthesisToggle: "دمج وتلخيص نهائي عبر Claude",
        sendPromptBtn: "بث السؤال وتجميع الردود",
        progressTitle: "جاري تشغيل عملية البث والتجميع...",
        stepBroadcast: "بث السؤال للتبويبات المفتوحة...",
        stepCollect: "انتظار تجميع الإجابات (ChatGPT, Gemini, DeepSeek)...",
        stepSynth: "إرسال الإجابات لـ Claude للتلخيص الموحد...",
        unifiedAnswerTitle: "الإجابة النهائية الموحدة والمعززة (Claude Synthesized)",
        copyBtn: "نسخ",
        chatgptAnswer: "إجابة ChatGPT",
        geminiAnswer: "إجابة Gemini",
        deepseekAnswer: "إجابة DeepSeek",
        footerText: "مبني محلياً بنسبة 100% بدون APIs مدفوعة",
        clearHistoryBtn: "مسح السجل",
        clearHistoryConfirm: "هل أنت متأكد من مسح السجل بالكامل؟",
        modalAlertTitle: "تنبيه",
        modalAlertMsg: "يرجى التأكد من تشغيل المتصفح وفتح التبويبات المطلوبة.",
        modalCancelBtn: "إلغاء",
        modalOkBtn: "موافق",
        
        alertError: "خطأ",
        alertSuccess: "تم بنجاح",
        alertSelectAgent: "الرجاء اختيار مساعد ذكاء اصطناعي واحد على الأقل.",
        alertEnterQuestion: "الرجاء كتابة سؤالك قبل الإرسال.",
        alertCopySuccess: "تم نسخ النص إلى الحافظة!",
        alertBrowserAlreadyOpenTitle: "المتصفح مفتوح بالفعل",
        alertBrowserAlreadyOpenMsg: "يبدو أن متصفح BRAVE مفتوح بالفعل بشكل عادي. لكي يتمكن البرنامج من التحكم بالتبويبات، يجب إغلاق جميع نوافذ المتصفح بالكامل وإعادة تشغيله في وضع التحكم.\n\nهل تريد من البرنامج إغلاق المتصفح وإعادة تشغيله تلقائياً؟ (سيتطلب منك المتصفح \"Restore\" لاستعادة تبويباتك المفتوحة)",
        alertSyncTitle: "تفعيل وضع التحكم والمزامنة",
        alertSyncMsg: "لكي يتمكن البرنامج من التحكم بالتبويبات ومزامنتها، يجب إغلاق متصفح BRAVE بالكامل وإعادة تشغيله في وضع التحكم.\n\nهل تريد إغلاق المتصفح الآن وإعادة فتحه؟",
        alertLaunchError: "حدث خطأ غير متوقع أثناء تشغيل المتصفح. تأكد من إغلاق أي جلسات تصفح اخري للمتصفح المختار.",
        uploadBtnTitle: "إرفاق صور أو مستندات",
        fileSizeError: "حجم الملف كبير جداً (الحد الأقصى 15 ميجابايت)",
        
        syncing: "جاري المزامنة...",
        syncSuccess: "تمت المزامنة وفتح التبويبات بنجاح. يرجى تسجيل الدخول بها يدوياً إذا لزم الأمر.",
        alertWarning: "تنبيه",
        enterQuestionFirst: "يرجى كتابة سؤالك أولاً.",
        selectOneAgent: "يرجى اختيار ذكاء اصطناعي واحد على الأقل للبث إليه.",
        stepBroadcastLoading: "جاري بث السؤال للتبويبات المفتوحة...",
        stepCollectPending: "انتظار تجميع الإجابات (ChatGPT, Gemini, DeepSeek)...",
        stepSynthPending: "إرسال الإجابات لـ Claude للتلخيص الموحد...",
        broadcastingAndCollecting: "جاري البث والتجميع...",
        stepBroadcastCompleted: "تم بث السؤال لجميع التبويبات.",
        stepCollectLoading: "جاري انتظار ردود المساعدين وكشطها...",
        errorProcessing: "حدث خطأ أثناء معالجة الطلب.",
        stepCollectCompleted: "تم استخراج ردود المساعدين بنجاح.",
        stepSynthLoading: "جاري توحيد الإجابات وصياغتها عبر Claude...",
        stepSynthCompleted: "تم الدمج والتلخيص بنجاح.",
        stepSynthSkippedMissing: "تم تخطي التلخيص لعدم توفر تبويب Claude.",
        stepSynthSkippedOff: "تم إيقاف خيار التلخيص.",
        operationFailedTitle: "فشل العملية",
        operationFailedMsg: "فشلت عملية البث وتجميع البيانات.",
        copied: "تم النسخ!",
        themeBtnDark: "مظلم",
        themeBtnLight: "فاتح",
        statusDisabled: "تم إيقاف هذا الموديل في الخيارات.",
        statusNoAnswer: "لم يقم هذا الموديل بإرجاع أي إجابة أو حدث خطأ.",

        modeInstant: "Instant",
        modeExpert: "DeepThink",
        selectAssistantLabel: "اختر المساعد الفردي للدردشة معه:",
        toggleSidebarTitle: "تبديل القائمة الجانبية",
        searchChatsTitle: "البحث في المحادثات",
        newChatBtnTitle: "محادثة جديدة",
        searchHistoryPlaceholder: "البحث في المحادثات...",
        welcomeInstant: "Start chatting with Instant",
        welcomeExpert: "Start chatting with DeepThink",
        promptPlaceholderChatgpt: "Message ChatGPT...",
        promptPlaceholderGemini: "Message Gemini...",
        promptPlaceholderDeepseek: "Message DeepSeek..."
    },
    en: {
        pageTitle: "AI Spark | Smart Coordinator",
        subTitle: "Local Smart Coordinator",
        braveBrowser: "Brave Browser",
        syncBtn: "Sync",
        refreshBtn: "Refresh",
        historyBtn: "History",
        newChatBtn: "New chat",
        today: "Today",
        yesterday: "Yesterday",
        previous7: "Previous 7 Days",
        older: "Older",
        dashboardTitle: "Distributed Broadcast Dashboard",
        dashboardDesc: "Type your question and the system will broadcast it concurrently to ChatGPT, Gemini, and DeepSeek, then collect and summarize it locally via Claude.",
        promptPlaceholder: "Type your question here in detail... (e.g. Explain cloud computing and its types?)",
        claudeSynthesisToggle: "Final merge and summarize via Claude",
        sendPromptBtn: "Broadcast Question & Collect Responses",
        progressTitle: "Running broadcast and collection process...",
        stepBroadcast: "Broadcasting question to open tabs...",
        stepCollect: "Waiting to collect answers (ChatGPT, Gemini, DeepSeek)...",
        stepSynth: "Sending answers to Claude for unified summary...",
        unifiedAnswerTitle: "Unified and Enhanced Final Answer (Claude Synthesized)",
        copyBtn: "Copy",
        chatgptAnswer: "ChatGPT Answer",
        geminiAnswer: "Gemini Answer",
        deepseekAnswer: "DeepSeek Answer",
        footerText: "100% locally built without paid APIs",
        clearHistoryBtn: "Clear History",
        clearHistoryConfirm: "Are you sure you want to clear all chat history?",
        modalAlertTitle: "Alert",
        modalAlertMsg: "Please ensure the browser is running and required tabs are open.",
        modalCancelBtn: "Cancel",
        modalOkBtn: "OK",
        
        alertError: "Error",
        alertSuccess: "Success",
        alertSelectAgent: "Please select at least one AI assistant.",
        alertEnterQuestion: "Please write your question before sending.",
        alertCopySuccess: "Text copied to clipboard!",
        alertBrowserAlreadyOpenTitle: "Browser Already Open",
        alertBrowserAlreadyOpenMsg: "It seems BRAVE is already open normally. For the program to control the tabs, all browser windows must be fully closed and restarted in control mode.\n\nDo you want the program to close the browser and restart it automatically? (The browser will ask you to \"Restore\" open tabs)",
        alertSyncTitle: "Activate Control & Sync Mode",
        alertSyncMsg: "For the program to control and sync tabs, BRAVE must be fully closed and restarted in control mode.\n\nDo you want to close the browser now and reopen it?",
        alertLaunchError: "An unexpected error occurred while launching the browser. Make sure to close any other browsing sessions.",
        uploadBtnTitle: "Attach photos or documents",
        fileSizeError: "File is too large (maximum 15MB)",
        
        is_instant_session: false,
        syncing: "Syncing...",
        syncSuccess: "Sync and tabs opening completed successfully. Please login manually if needed.",
        alertWarning: "Warning",
        enterQuestionFirst: "Please type your question first.",
        selectOneAgent: "Please select at least one AI to broadcast to.",
        stepBroadcastLoading: "Broadcasting question to open tabs...",
        stepCollectPending: "Waiting to collect answers (ChatGPT, Gemini, DeepSeek)...",
        stepSynthPending: "Sending answers to Claude for unified summary...",
        broadcastingAndCollecting: "Broadcasting and Collecting...",
        stepBroadcastCompleted: "Question broadcasted to all tabs.",
        stepCollectLoading: "Waiting for and scraping AI responses...",
        errorProcessing: "An error occurred while processing the request.",
        stepCollectCompleted: "AI responses extracted successfully.",
        stepSynthLoading: "Unifying and synthesizing answers via Claude...",
        stepSynthCompleted: "Synthesis and merge completed successfully.",
        stepSynthSkippedMissing: "Synthesis skipped because Claude tab is unavailable.",
        stepSynthSkippedOff: "Synthesis option is disabled.",
        operationFailedTitle: "Operation Failed",
        operationFailedMsg: "Failed to broadcast and collect data.",
        copied: "Copied!",
        themeBtnDark: "Dark",
        themeBtnLight: "Light",
        statusDisabled: "This model was disabled in the options.",
        statusNoAnswer: "This model did not return any answer or an error occurred.",

        modeInstant: "Instant",
        modeExpert: "DeepThink",
        selectAssistantLabel: "Choose an assistant for single chat:",
        toggleSidebarTitle: "Toggle Sidebar",
        searchChatsTitle: "Search Chats",
        newChatBtnTitle: "New Chat",
        searchHistoryPlaceholder: "Search chats...",
        welcomeInstant: "Start chatting with Instant",
        welcomeExpert: "Start chatting with DeepThink",
        promptPlaceholderChatgpt: "Message ChatGPT...",
        promptPlaceholderGemini: "Message Gemini...",
        promptPlaceholderDeepseek: "Message DeepSeek..."
    },
    fr: {
        pageTitle: "AI Spark | Coordinateur Intelligent",
        subTitle: "Coordinateur Intelligent Local",
        braveBrowser: "Navigateur Brave",
        syncBtn: "Synchroniser",
        refreshBtn: "Actualiser",
        historyBtn: "Historique",
        newChatBtn: "Nouveau chat",
        today: "Aujourd'hui",
        yesterday: "Hier",
        previous7: "Les 7 jours précédents",
        older: "Plus ancien",
        dashboardTitle: "Tableau de Bord de Diffusion Distribuée",
        dashboardDesc: "Tapez votre question et le système la diffusera simultanément sur ChatGPT, Gemini et DeepSeek, puis la collectera et la résumera localement via Claude.",
        promptPlaceholder: "Tapez votre question ici en détail... (ex. Expliquez le cloud computing et ses types ?)",
        claudeSynthesisToggle: "Fusion finale et résumé via Claude",
        sendPromptBtn: "Diffuser la Question & Collecter les Réponses",
        progressTitle: "Exécution du processus de diffusion et de collecte...",
        stepBroadcast: "Diffusion de la question aux onglets ouverts...",
        stepCollect: "En attente des réponses (ChatGPT, Gemini, DeepSeek)...",
        stepSynth: "Envoi des réponses à Claude pour un résumé unifié...",
        unifiedAnswerTitle: "Réponse Finale Unifiée et Améliorée (Synthèse Claude)",
        copyBtn: "Copier",
        chatgptAnswer: "Réponse ChatGPT",
        geminiAnswer: "Réponse Gemini",
        deepseekAnswer: "Réponse DeepSeek",
        footerText: "Construit 100% localement sans API payantes",
        clearHistoryBtn: "Effacer l'historique",
        clearHistoryConfirm: "Êtes-vous sûr de vouloir effacer tout l'historique ?",
        modalAlertTitle: "Alerte",
        modalAlertMsg: "Veuillez vous assurer que le navigateur est en cours d'exécution et que les onglets requis sont ouverts.",
        modalCancelBtn: "Annuler",
        modalOkBtn: "OK",
        
        alertError: "Erreur",
        alertSuccess: "Succès",
        alertSelectAgent: "Veuillez sélectionner au moins un assistant IA.",
        alertEnterQuestion: "Veuillez écrire votre question avant de l'envoyer.",
        alertCopySuccess: "Texte copié dans le presse-papiers !",
        alertBrowserAlreadyOpenTitle: "Navigateur Déjà Ouvert",
        alertBrowserAlreadyOpenMsg: "Il semble que BRAVE soit déjà ouvert normalement. Pour que le programme contrôle les onglets, toutes les fenêtres du navigateur doivent être complètement fermées et redémarrées en mode de contrôle.\n\nVoulez-vous que le programme ferme le navigateur et le redémarre automatiquement ? (Le navigateur vous demandera de « Restaurer » les onglets ouverts)",
        alertSyncTitle: "Activer le Mode de Contrôle & Synchronisation",
        alertSyncMsg: "Pour que le programme contrôle et synchronise les onglets, BRAVE doit être complètement fermé et redémarré en mode de contrôle.\n\nVoulez-vous fermer le navigateur maintenant et le rouvrir ?",
        alertLaunchError: "Une erreur inattendue s'est produite lors du lancement du navigateur. Assurez-vous de fermer toutes les autres sessions de navigation.",
        uploadBtnTitle: "Joindre des photos ou documents",
        fileSizeError: "Le fichier est trop volumineux (maximum 15 Mo)",
        
        syncing: "Synchronisation...",
        syncSuccess: "Synchronisation et ouverture des onglets terminées avec succès. Veuillez vous connecter manuellement si nécessaire.",
        alertWarning: "Alerte",
        enterQuestionFirst: "Veuillez d'abord taper votre question.",
        selectOneAgent: "Veuillez sélectionner au moins une IA à laquelle diffuser.",
        stepBroadcastLoading: "Diffusion de la question aux onglets ouverts...",
        stepCollectPending: "En attente de collecter les réponses (ChatGPT, Gemini, DeepSeek)...",
        stepSynthPending: "Envoi des réponses à Claude pour résumé unifié...",
        broadcastingAndCollecting: "Diffusion et Collecte...",
        stepBroadcastCompleted: "Question diffusée à tous les onglets.",
        stepCollectLoading: "En attente et récupération des réponses des IA...",
        errorProcessing: "Une erreur s'est produite lors du traitement de la requête.",
        stepCollectCompleted: "Réponses des IA extraites avec succès.",
        stepSynthLoading: "Unification et synthèse des réponses via Claude...",
        stepSynthCompleted: "Synthèse et fusion terminées avec succès.",
        stepSynthSkippedMissing: "Synthèse ignorée car l'onglet Claude est indisponible.",
        stepSynthSkippedOff: "L'option de synthèse est désactivée.",
        operationFailedTitle: "Échec de l'Opération",
        operationFailedMsg: "Échec de la diffusion et de la collecte des données.",
        copied: "Copié !",
        themeBtnDark: "Sombre",
        themeBtnLight: "Clair",
        statusDisabled: "Ce modèle a été désactivé dans les options.",
        statusNoAnswer: "Ce modèle n'a renvoyé aucune réponse ou une erreur s'est produite.",

        modeInstant: "Instant",
        modeExpert: "DeepThink",
        selectAssistantLabel: "Choisissez un assistant pour le chat unique:",
        toggleSidebarTitle: "Basculer la barre latérale",
        searchChatsTitle: "Rechercher des discussions",
        newChatBtnTitle: "Nouveau chat",
        searchHistoryPlaceholder: "Rechercher des discussions...",
        welcomeInstant: "Start chatting with Instant",
        welcomeExpert: "Start chatting with DeepThink",
        promptPlaceholderChatgpt: "Message ChatGPT...",
        promptPlaceholderGemini: "Message Gemini...",
        promptPlaceholderDeepseek: "Message DeepSeek..."
    }
};

// Safe localStorage wrapper to prevent crashes in private browsing or restricted environments
const safeStorage = {
    getItem(key, defaultValue) {
        try {
            return localStorage.getItem(key) || defaultValue;
        } catch (e) {
            console.warn("localStorage is not accessible, using default value.", e);
            return defaultValue;
        }
    },
    setItem(key, value) {
        try {
            localStorage.setItem(key, value);
        } catch (e) {
            console.warn("localStorage is not accessible, value not saved.", e);
        }
    }
};

let currentLang = safeStorage.getItem("appLang", "ar");
let currentTheme = safeStorage.getItem("appTheme", "dark");

function updateTheme(theme) {
    currentTheme = theme;
    safeStorage.setItem("appTheme", theme);
    const htmlRoot = document.getElementById("html-root");
    const themeBtn = document.getElementById("theme-toggle");
    if (htmlRoot) {
        htmlRoot.setAttribute("data-theme", theme);
    }
    if (themeBtn) {
        const icon = themeBtn.querySelector("i");
        const span = themeBtn.querySelector("span");
        if (theme === "dark") {
            icon.className = "fa-solid fa-moon";
            if (span && translations[currentLang]) span.textContent = translations[currentLang].themeBtnDark;
        } else {
            icon.className = "fa-solid fa-sun";
            if (span && translations[currentLang]) span.textContent = translations[currentLang].themeBtnLight;
        }
    }
}

function updateLanguage(lang) {
    currentLang = lang;
    safeStorage.setItem("appLang", lang);
    const htmlRoot = document.getElementById("html-root");
    if (htmlRoot) {
        if (lang === "ar") {
            htmlRoot.setAttribute("dir", "rtl");
            htmlRoot.setAttribute("lang", "ar");
        } else {
            htmlRoot.setAttribute("dir", "ltr");
            htmlRoot.setAttribute("lang", lang);
        }
    }
    
    document.querySelectorAll("[data-i18n]").forEach(el => {
        const key = el.getAttribute("data-i18n");
        if (translations[lang] && translations[lang][key]) {
            el.innerHTML = translations[lang][key];
        }
    });
    
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
        const key = el.getAttribute("data-i18n-placeholder");
        if (translations[lang] && translations[lang][key]) {
            el.setAttribute("placeholder", translations[lang][key]);
        }
    });

    document.querySelectorAll("[data-i18n-title]").forEach(el => {
        const key = el.getAttribute("data-i18n-title");
        if (translations[lang] && translations[lang][key]) {
            el.setAttribute("title", translations[lang][key]);
        }
    });
    
    const selector = document.getElementById("language-selector");
    if (selector) selector.value = lang;
    
    // Update theme button translation
    updateTheme(currentTheme);
    
    // Recalculate mode switcher bubble position after layout update
    setTimeout(updateModeBubble, 50);
}

// DOM Elements
const launchBrowserBtn = document.getElementById("launch-browser-btn");
const clearHistoryBtn = document.getElementById("clear-history-btn");
const sendPromptBtn = document.getElementById("send-prompt-btn");
const promptTextarea = document.getElementById("prompt-textarea");
const themeToggleBtn = document.getElementById("theme-toggle");
const centerWrapper = document.getElementById("center-wrapper");
const resultsArea = document.getElementById("results-area");
const uploadFileBtn = document.getElementById("upload-file-btn");
const fileInput = document.getElementById("file-input");
const filePreviewContainer = document.getElementById("file-preview-container");

// Tab status elements
const statusBrowser = document.getElementById("status-browser");

// Checkboxes and toggles
const checkChatgpt = document.getElementById("check-chatgpt");
const checkGemini = document.getElementById("check-gemini");
const checkDeepseek = document.getElementById("check-deepseek");
const toggleSynthesis = document.getElementById("toggle-synthesis");

// Progress container and steps
const progressContainer = document.getElementById("progress-container");
const stepBroadcast = document.getElementById("step-broadcast");
const stepCollect = document.getElementById("step-collect");
const stepSynth = document.getElementById("step-synth");

// Response containers
const cardChatgpt = document.getElementById("card-chatgpt");
const cardGemini = document.getElementById("card-gemini");
const cardDeepseek = document.getElementById("card-deepseek");
const unifiedAnswerContainer = document.getElementById("unified-answer-container");
const textChatgpt = document.getElementById("text-chatgpt");
const textGemini = document.getElementById("text-gemini");
const textDeepseek = document.getElementById("text-deepseek");
const unifiedText = document.getElementById("unified-text");

// Modal elements
const modal = document.getElementById("modal");
const modalTitle = document.getElementById("modal-title");
const modalMessage = document.getElementById("modal-message");
const closeModalBtn = document.getElementById("close-modal-btn");
const modalOkBtn = document.getElementById("modal-ok-btn");
const modalCancelBtn = document.getElementById("modal-cancel-btn");

// Global callback pointers for modal buttons
let modalConfirmCallback = null;
let modalCancelCallback = null;

// Initialization
function initApp() {
    // Hide splash loader after 3 seconds
    setTimeout(() => {
        const splashLoader = document.getElementById("splash-loader");
        if (splashLoader) {
            splashLoader.classList.add("fade-out");
            setTimeout(() => {
                splashLoader.remove();
            }, 500);
        }
    }, 3000);
    
    updateLanguage(currentLang);
    updateTheme(currentTheme);
    
    const langSelector = document.getElementById("language-selector");
    if (langSelector) {
        langSelector.addEventListener("change", (e) => {
            updateLanguage(e.target.value);
        });
    }
    
    checkStatus().then(() => {
        initAITabs();
    });
    loadHistory();
    
    // Auto-refresh status every 4 seconds
    setInterval(checkStatus, 4000);
    
    // Event Listeners
    if (launchBrowserBtn) {
        launchBrowserBtn.addEventListener("click", () => {
            if (!isBrowserConnected) {
                // Browser is not connected in debug mode.
                // Immediately prompt user to close and restart the browser, bypassing initial duplicate window launch call.
                showConfirmAlert(
                    translations[currentLang].alertSyncTitle,
                    translations[currentLang].alertSyncMsg,
                    () => {
                        launchBrowser(true, false);
                    }
                );
            } else {
                // Already connected in debug mode, just open/sync the tabs
                launchBrowser(false, false);
            }
        });
    }
    
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener("click", clearHistory);
    }
    
        const newChatBtn = document.getElementById("new-chat-btn");
        if (newChatBtn) {
            newChatBtn.addEventListener("click", handleNewChat);
        }

        const newChatBtnTop = document.getElementById("new-chat-btn-top");
        if (newChatBtnTop) {
            newChatBtnTop.addEventListener("click", handleNewChat);
        }

        // Sidebar toggle button
        const toggleSidebarBtn = document.getElementById("toggle-sidebar-btn");
        const sidebar = document.querySelector(".sidebar");
        if (toggleSidebarBtn && sidebar) {
            toggleSidebarBtn.addEventListener("click", () => {
                sidebar.classList.toggle("collapsed");
            });
        }

        // Sidebar search button
        const searchHistoryBtn = document.getElementById("search-history-btn");
        const sidebarSearchBox = document.getElementById("sidebar-search-box");
        const searchHistoryInput = document.getElementById("search-history-input");
        if (searchHistoryBtn && sidebarSearchBox) {
            searchHistoryBtn.addEventListener("click", () => {
                if (sidebar && sidebar.classList.contains("collapsed")) {
                    sidebar.classList.remove("collapsed");
                }
                sidebarSearchBox.classList.toggle("hidden");
                if (!sidebarSearchBox.classList.contains("hidden") && searchHistoryInput) {
                    searchHistoryInput.focus();
                } else if (searchHistoryInput) {
                    searchHistoryInput.value = "";
                    filterHistoryList("");
                }
            });
        }

        // Real-time search history filtering
        if (searchHistoryInput) {
            searchHistoryInput.addEventListener("input", (e) => {
                const query = e.target.value.toLowerCase().trim();
                filterHistoryList(query);
            });
        }

        // Switcher mode buttons
        const modeInstantBtn = document.getElementById("mode-instant-btn");
        const modeExpertBtn = document.getElementById("mode-expert-btn");
        if (modeInstantBtn) {
            modeInstantBtn.addEventListener("click", () => setMode("instant"));
        }
        if (modeExpertBtn) {
            modeExpertBtn.addEventListener("click", () => setMode("expert"));
        }

        // Assistant selection cards
        const assistantCards = document.querySelectorAll(".assistant-card");
        assistantCards.forEach(card => {
            card.addEventListener("click", () => {
                assistantCards.forEach(c => c.classList.remove("active"));
                card.classList.add("active");
                activeInstantAssistant = card.getAttribute("data-assistant");
                updatePromptPlaceholder();
            });
        });
    
    if (sendPromptBtn) {
        sendPromptBtn.addEventListener("click", sendPrompt);
    }

    if (promptTextarea) {
        promptTextarea.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendPrompt();
            }
        });
    }

    if (uploadFileBtn && fileInput) {
        uploadFileBtn.addEventListener("click", () => {
            fileInput.click();
        });
        fileInput.addEventListener("change", handleFileSelection);
    }
    
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            updateTheme(newTheme);
        });
    }
    
    // Sticky prompt remains permanently anchored at the bottom (scroll-hiding disabled)
    
    // Modal events
    if (modalOkBtn) {
        modalOkBtn.addEventListener("click", () => {
            hideModal();
            if (modalConfirmCallback) {
                modalConfirmCallback();
                modalConfirmCallback = null;
            }
        });
    }
    if (modalCancelBtn) {
        modalCancelBtn.addEventListener("click", () => {
            hideModal();
            if (modalCancelCallback) {
                modalCancelCallback();
                modalCancelCallback = null;
            }
        });
    }
    if (closeModalBtn) {
        closeModalBtn.addEventListener("click", () => {
            hideModal();
            if (modalCancelCallback) {
                modalCancelCallback();
                modalCancelCallback = null;
            }
        });
    }
    window.addEventListener("click", (e) => {
        if (e.target === modal) {
            hideModal();
            if (modalCancelCallback) {
                modalCancelCallback();
                modalCancelCallback = null;
            }
        }
    });

    // Listen to window resize events to adjust switcher bubble position dynamically
    window.addEventListener("resize", updateModeBubble);

    // Initial positioning of switcher bubble
    setTimeout(updateModeBubble, 150);
}

// Ensure the app starts even if DOMContentLoaded has already fired
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initApp);
} else {
    initApp();
}

// Check status of browser connection and open tabs
async function checkStatus() {
    try {
        const response = await fetch("/api/status");
        const status = await response.json();
        
        isBrowserConnected = status.connected;
        
        // Update browser status indicator
        if (statusBrowser) updateStatusIndicator(statusBrowser, isBrowserConnected);
        
        const browserIconEl = document.getElementById("browser-icon");
        const browserNameEl = document.getElementById("browser-name");
        if (browserIconEl && browserNameEl && status.browser) {
            browserIconEl.src = `/static/icons/${status.browser}.svg`;
            browserIconEl.alt = status.browser;
            browserNameEl.textContent = status.browser;
            if (statusBrowser) {
                statusBrowser.title = status.browser;
            }
        }
        

        
        // If not connected, disable prompt send button to avoid errors
        if (!isBrowserConnected) {
            sendPromptBtn.disabled = true;
            sendPromptBtn.style.opacity = 0.5;
            sendPromptBtn.title = translations[currentLang].modalAlertMsg;
        } else {
            sendPromptBtn.disabled = false;
            sendPromptBtn.style.opacity = 1;
            sendPromptBtn.title = "";
        }
    } catch (err) {
        console.error("Error checking status:", err);
    }
}

function updateStatusIndicator(element, isOnline) {
    if (isOnline) {
        element.classList.add("online");
    } else {
        element.classList.remove("online");
    }
}

// Automatically initialize AI tabs if they are missing or browser is not connected
async function initAITabs() {
    try {
        const response = await fetch("/api/status");
        const status = await response.json();
        
        // Check if any tab is missing or browser is disconnected
        const anyTabMissing = !status.tabs.chatgpt || !status.tabs.gemini || !status.tabs.deepseek || !status.tabs.claude;
        
        if (!status.connected || anyTabMissing) {
            console.log("Browser disconnected or AI tabs missing. Automatically initializing...");
            // Call launchBrowser silently on startup/load. If the port is open, this connects Playwright and opens any missing tabs.
            await launchBrowser(false, true);
        } else {
            // Browser is already connected. Reset open tabs silently to start on a new chat.
            console.log("Browser is connected. Resetting tabs to start with a new chat...");
            try {
                await fetch("/api/browser/new_chat", { method: "POST" });
            } catch (e) {
                console.error("Failed to reset browser tabs for new chat:", e);
            }
        }
    } catch (err) {
        console.error("Auto tab initialization failed:", err);
    }
}

// Launch browser with CDP and open tabs
async function launchBrowser(forceKill = false, silent = false) {
    if (!silent) {
        launchBrowserBtn.disabled = true;
        launchBrowserBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span>${translations[currentLang].syncing}</span>`;
    }
    
    try {
        const response = await fetch("/api/browser/launch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ force_kill: forceKill })
        });
        const data = await response.json();
        
        if (response.ok) {
            if (!silent) {
                showAlert(translations[currentLang].alertSuccess, translations[currentLang].syncSuccess);
            }
        } else {
            // Check if error indicates browser is already open
            if (data.detail && (data.detail.includes("إغلاق") || data.detail.includes("close") || data.detail.includes("running"))) {
                if (!silent) {
                    showConfirmAlert(
                        translations[currentLang].alertBrowserAlreadyOpenTitle,
                        translations[currentLang].alertBrowserAlreadyOpenMsg,
                        () => {
                            launchBrowser(true, false);
                        }
                    );
                }
            } else {
                if (!silent) {
                    showAlert(translations[currentLang].alertError, data.detail || "Launch failed.");
                }
            }
        }
    } catch (err) {
        console.error("Error launching browser:", err);
        if (!silent) {
            showAlert(translations[currentLang].alertError, translations[currentLang].alertLaunchError);
        }
    } finally {
        if (!silent) {
            launchBrowserBtn.innerHTML = `<i class="fa-solid fa-arrows-spin"></i> <span>${translations[currentLang].syncBtn}</span>`;
            launchBrowserBtn.disabled = false;
        }
        checkStatus();
    }
}

// Helper Functions for Chat History
async function saveHistory(turnData) {
    try {
        await fetch("/api/history", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(turnData)
        });
    } catch (e) {
        console.error("Failed to save history", e);
    }
}

async function loadHistory() {
    try {
        const response = await fetch("/api/history");
        const data = await response.json();
        if (data.status === "success" && data.history) {
            chatHistory = data.history;
            
            // Do not load the last active chat on startup/load.
            // This ensures we always start on a clean "New Chat" screen.
            currentSessionId = Date.now().toString();
            
            renderActiveSession();
            renderSidebarHistory(chatHistory);
        }
    } catch (e) {
        console.error("Failed to load history", e);
    }
}

function renderActiveSession() {
    const chatContainer = document.getElementById("chat-history");
    if (!chatContainer) return;
    chatContainer.innerHTML = "";
    
    const activeTurns = chatHistory.filter(turn => (turn.session_id || turn.id.toString()) === currentSessionId);
    
    const aiToggles = document.querySelector(".ai-toggles");
    const instantAssistants = document.getElementById("instant-assistants");
    
    if (activeTurns.length > 0) {
        activeTurns.forEach(turn => {
            const turnEl = renderTurn(turn);
            turnEl.id = `turn-${turn.id}`;
            chatContainer.appendChild(turnEl);
        });
        chatContainer.classList.remove("hidden");
        centerWrapper.classList.add("has-results");
        setTimeout(scrollToBottom, 100);
        
        // Restore mode & toggle checkboxes from first turn
        const firstTurn = activeTurns[0];
        const isInstant = firstTurn.agents && firstTurn.agents.length === 1 && !firstTurn.synthesize;
        
        if (isInstant) {
            activeMode = "instant";
            activeInstantAssistant = firstTurn.agents[0];
            if (aiToggles) aiToggles.classList.add("hidden");
        } else {
            activeMode = "expert";
            if (aiToggles) aiToggles.classList.remove("hidden");
            
            // Update checkbox state
            if (checkChatgpt) checkChatgpt.checked = firstTurn.agents.includes("chatgpt");
            if (checkGemini) checkGemini.checked = firstTurn.agents.includes("gemini");
            if (checkDeepseek) checkDeepseek.checked = firstTurn.agents.includes("deepseek");
            if (toggleSynthesis) toggleSynthesis.checked = !!firstTurn.synthesize;
        }
    } else {
        chatContainer.classList.add("hidden");
        centerWrapper.classList.remove("has-results");
        setMode(activeMode);
    }
    updatePromptPlaceholder();
}

function renderSidebarHistory(history) {
    const listContainer = document.getElementById("sidebar-history-list");
    if (!listContainer) return;
    listContainer.innerHTML = "";
    
    // Group turns by session_id
    const sessionsMap = {};
    history.forEach(turn => {
        const sId = turn.session_id || turn.id.toString();
        if (!sessionsMap[sId]) {
            sessionsMap[sId] = [];
        }
        sessionsMap[sId].push(turn);
    });
    
    const sessionsList = [];
    for (const [sId, turns] of Object.entries(sessionsMap)) {
        if (turns.length === 0) continue;
        const firstTurn = turns[0];
        sessionsList.push({
            id: sId,
            timestamp: firstTurn.id,
            title: firstTurn.question || "Chat",
            turns: turns
        });
    }
    
    // Sort descending (newest sessions first)
    sessionsList.sort((a, b) => b.timestamp - a.timestamp);
    
    const groups = {
        "Today": [],
        "Yesterday": [],
        "Previous 7 Days": [],
        "Older": []
    };
    
    const groupTranslates = {
        "Today": translations[currentLang]?.today || "Today",
        "Yesterday": translations[currentLang]?.yesterday || "Yesterday",
        "Previous 7 Days": translations[currentLang]?.previous7 || "Previous 7 Days",
        "Older": translations[currentLang]?.older || "Older"
    };

    const now = new Date();
    const todayStr = now.toDateString();
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = yesterday.toDateString();
    
    const sevenDaysAgo = new Date(now);
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    
    sessionsList.forEach(session => {
        const sessionDate = new Date(session.timestamp);
        if (isNaN(sessionDate.getTime())) {
            groups["Older"].push(session);
            return;
        }
        
        if (sessionDate.toDateString() === todayStr) {
            groups["Today"].push(session);
        } else if (sessionDate.toDateString() === yesterdayStr) {
            groups["Yesterday"].push(session);
        } else if (sessionDate > sevenDaysAgo) {
            groups["Previous 7 Days"].push(session);
        } else {
            const monthStr = `${sessionDate.getFullYear()}-${String(sessionDate.getMonth() + 1).padStart(2, '0')}`;
            if (!groups[monthStr]) {
                groups[monthStr] = [];
            }
            groups[monthStr].push(session);
        }
    });
    
    for (const [groupName, items] of Object.entries(groups)) {
        if (items.length === 0) continue;
        
        const titleText = groupTranslates[groupName] || groupName;
        
        const groupTitle = document.createElement("div");
        groupTitle.className = "history-group-title";
        groupTitle.textContent = titleText;
        listContainer.appendChild(groupTitle);
        
        items.forEach(session => {
            const el = document.createElement("div");
            el.className = "history-item";
            if (session.id === currentSessionId) {
                el.classList.add("active");
            }
            el.style.display = "flex";
            el.style.alignItems = "center";
            el.style.gap = "8px";
            el.title = session.title;
            
            const icon = document.createElement("i");
            icon.className = "fa-regular fa-message";
            icon.style.fontSize = "12px";
            icon.style.flexShrink = "0";
            
            const textSpan = document.createElement("span");
            textSpan.textContent = session.title;
            textSpan.style.overflow = "hidden";
            textSpan.style.textOverflow = "ellipsis";
            textSpan.style.whiteSpace = "nowrap";
            
            el.appendChild(icon);
            el.appendChild(textSpan);
            
            el.onclick = () => {
                currentSessionId = session.id;
                document.querySelectorAll(".history-item").forEach(itemEl => {
                    itemEl.classList.remove("active");
                });
                el.classList.add("active");
                renderActiveSession();
            };
            listContainer.appendChild(el);
        });
    }
}

function clearHistory() {
    const confirmMsg = translations[currentLang]?.clearHistoryConfirm || "Are you sure you want to clear all chat history?";
    showConfirmAlert(translations[currentLang].alertWarning, confirmMsg, async () => {
        try {
            await fetch("/api/history", { method: "DELETE" });
            chatHistory = [];
            document.getElementById("chat-history").innerHTML = "";
            document.getElementById("chat-history").classList.add("hidden");
            centerWrapper.classList.remove("has-results");
            renderSidebarHistory(chatHistory);
        } catch (e) {
            console.error("Failed to clear history", e);
        }
    });
}

// Safe scroll to bottom helper
function scrollToBottom() {
    const mainContent = document.querySelector(".main-content");
    if (mainContent) {
        mainContent.scrollTo({
            top: mainContent.scrollHeight,
            behavior: 'smooth'
        });
    }
}

function renderTurn(turnData) {
    const template = document.getElementById("chat-turn-template");
    const clone = template.content.cloneNode(true);
    const turnEl = clone.querySelector(".chat-turn");
    
    // Set user message
    const userMsg = turnEl.querySelector(".user-message-bubble");
    userMsg.textContent = turnData.question;
    
    // Set AI responses
    const aiContainer = turnEl.querySelector(".ai-responses-container");
    
    // Helper to setup card
    const setupCard = (agent, htmlContent) => {
        const card = aiContainer.querySelector(`.answer-card[data-ai="${agent}"]`);
        if (htmlContent) {
            card.classList.remove("hidden");
            const body = card.querySelector(".card-body");
            body.innerHTML = htmlContent;
            
            // Setup copy button
            const copyBtn = card.querySelector(".btn-copy");
            copyBtn.onclick = () => {
                const text = body.innerText;
                navigator.clipboard.writeText(text).then(() => {
                    showAlert(translations[currentLang].alertSuccess, translations[currentLang].alertCopySuccess);
                }).catch(() => {
                    // fallback
                    const textarea = document.createElement('textarea');
                    textarea.value = text;
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    textarea.remove();
                    showAlert(translations[currentLang].alertSuccess, translations[currentLang].alertCopySuccess);
                });
            };
        } else {
            card.remove(); // Remove unused cards
        }
    };
    
    // Claude Synthesized
    if (turnData.synthesize) {
        if (turnData.synthesized) {
            setupCard("unified", formatMarkdown(turnData.synthesized));
        } else {
            setupCard("unified", `<em style="color: var(--text-muted);">${translations[currentLang].statusNoAnswer}</em>`);
        }
    } else {
        const unifiedCard = aiContainer.querySelector('.answer-card[data-ai="unified"]');
        if (unifiedCard) unifiedCard.remove();
    }
    
    // ChatGPT
    if (!turnData.agents.includes("chatgpt")) {
        setupCard("chatgpt", null);
    } else if (turnData.responses && turnData.responses.chatgpt) {
        setupCard("chatgpt", formatMarkdown(turnData.responses.chatgpt));
    } else {
        setupCard("chatgpt", `<em style="color: var(--text-muted);">${translations[currentLang].statusNoAnswer}</em>`);
    }
    
    // Gemini
    if (!turnData.agents.includes("gemini")) {
        setupCard("gemini", null);
    } else if (turnData.responses && turnData.responses.gemini) {
        setupCard("gemini", formatMarkdown(turnData.responses.gemini));
    } else {
        setupCard("gemini", `<em style="color: var(--text-muted);">${translations[currentLang].statusNoAnswer}</em>`);
    }
    
    // DeepSeek
    if (!turnData.agents.includes("deepseek")) {
        setupCard("deepseek", null);
    } else if (turnData.responses && turnData.responses.deepseek) {
        setupCard("deepseek", formatMarkdown(turnData.responses.deepseek));
    } else {
        setupCard("deepseek", `<em style="color: var(--text-muted);">${translations[currentLang].statusNoAnswer}</em>`);
    }
    
    return turnEl;
}

// Send user query to selected AIs and synthesize response
async function sendPrompt() {
    const question = promptTextarea.value.trim();
    if (!question) {
        showAlert(translations[currentLang].alertWarning, translations[currentLang].enterQuestionFirst);
        return;
    }

    // Capture files and clear input immediately for instant feedback
    const filesToSend = [...selectedFiles];
    promptTextarea.value = "";
    selectedFiles = [];
    renderFilePreviews();
    
    // Determine selected agents
    const agents = [];
    let synthesize = false;
    
    if (activeMode === "instant") {
        agents.push(activeInstantAssistant);
        synthesize = false;
    } else {
        if (checkChatgpt.checked) agents.push("chatgpt");
        if (checkGemini.checked) agents.push("gemini");
        if (checkDeepseek.checked) agents.push("deepseek");
        synthesize = toggleSynthesis.checked;
    }
    
    if (agents.length === 0) {
        showAlert(translations[currentLang].alertWarning, translations[currentLang].selectOneAgent);
        return;
    }
    
    // Show and reset progress container
    progressContainer.classList.remove("hidden");
    
    const broadcastLabel = activeMode === "instant" 
        ? (currentLang === "ar" ? `جاري بث السؤال لـ ${agents[0].toUpperCase()}...` : `Broadcasting question to ${agents[0].toUpperCase()}...`)
        : translations[currentLang].stepBroadcastLoading;
        
    const collectLabel = activeMode === "instant"
        ? (currentLang === "ar" ? `انتظار تجميع إجابة ${agents[0].toUpperCase()}...` : `Waiting to collect answer from ${agents[0].toUpperCase()}...`)
        : translations[currentLang].stepCollectPending;
        
    setStepState(stepBroadcast, "loading", broadcastLabel);
    setStepState(stepCollect, "pending", collectLabel);
    setStepState(stepSynth, "pending", translations[currentLang].stepSynthPending);
    
    sendPromptBtn.disabled = true;
    sendPromptBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i>`;
    
    // Simulate step timing since HTTP is monolithic
    setTimeout(() => {
        const broadcastCompletedLabel = activeMode === "instant"
            ? (currentLang === "ar" ? `تم بث السؤال لـ ${agents[0].toUpperCase()}.` : `Question broadcasted to ${agents[0].toUpperCase()}.`)
            : translations[currentLang].stepBroadcastCompleted;
        setStepState(stepBroadcast, "completed", broadcastCompletedLabel);
        
        const collectLoadingLabel = activeMode === "instant"
            ? (currentLang === "ar" ? `جاري انتظار رد ${agents[0].toUpperCase()} وكشطه...` : `Waiting for and scraping ${agents[0].toUpperCase()} response...`)
            : translations[currentLang].stepCollectLoading;
        setStepState(stepCollect, "loading", collectLoadingLabel);
    }, 4000);
    
    try {
        const response = await fetch("/api/query", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question, agents, synthesize, files: filesToSend })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || translations[currentLang].errorProcessing);
        }
        
        const collectCompletedLabel = activeMode === "instant"
            ? (currentLang === "ar" ? `تم استخراج رد ${agents[0].toUpperCase()} بنجاح.` : `${agents[0].toUpperCase()} response extracted successfully.`)
            : translations[currentLang].stepCollectCompleted;
        setStepState(stepCollect, "completed", collectCompletedLabel);
        
        if (synthesize) {
            if (data.synthesized) {
                setStepState(stepSynth, "completed", translations[currentLang].stepSynthCompleted);
            } else {
                setStepState(stepSynth, "pending", translations[currentLang].stepSynthSkippedMissing);
            }
        } else {
            setStepState(stepSynth, "pending", translations[currentLang].stepSynthSkippedOff);
        }
        
        // Build Turn Data
        const turnData = {
            id: Date.now(),
            question: question,
            agents: agents,
            synthesize: synthesize,
            responses: data.responses,
            synthesized: data.synthesized,
            session_id: currentSessionId
        };
        
        // Add to history and DOM
        chatHistory.push(turnData);
        saveHistory(turnData);
        
        const chatContainer = document.getElementById("chat-history");
        chatContainer.classList.remove("hidden");
        centerWrapper.classList.add("has-results");
        
        const turnEl = renderTurn(turnData);
        turnEl.id = `turn-${turnData.id}`;
        chatContainer.appendChild(turnEl);
        
        renderSidebarHistory(chatHistory);
        
        setTimeout(scrollToBottom, 100);
        
    } catch (err) {
        console.error("Query execution failed:", err);
        showAlert(translations[currentLang].operationFailedTitle, err.message || translations[currentLang].operationFailedMsg);
    } finally {
        progressContainer.classList.add("hidden");
        sendPromptBtn.disabled = false;
        sendPromptBtn.innerHTML = `<i class="fa-solid fa-arrow-up"></i>`;
    }
}

// UI state update helper for progress steps
function setStepState(element, state, text) {
    const icon = element.querySelector("i");
    const span = element.querySelector("span");
    
    span.textContent = text;
    element.className = "step-item"; // reset class
    
    if (state === "loading") {
        element.classList.add("active");
        icon.className = "fa-solid fa-circle-notch fa-spin";
    } else if (state === "completed") {
        element.classList.add("completed");
        icon.className = "fa-solid fa-circle-check";
    } else {
        icon.className = "fa-regular fa-circle";
    }
}

function formatMarkdown(text) {
    if (!text) return "";
    
    // 1. Clean HTML to prevent XSS
    let html = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
        
    // 2. Extract code blocks to protect them from downstream paragraph formatting
    const codeBlocks = [];
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
        const placeholder = `<!--__CODE_BLOCK_${codeBlocks.length}__-->`;
        const languageLabel = lang ? lang.toLowerCase() : 'code';
        const formattedCode = `
<div class="code-block-wrapper" dir="ltr">
    <div class="code-block-header">
        <span class="code-lang">${languageLabel}</span>
        <button class="code-copy-btn" onclick="copyCodeBlock(this)" title="${translations[currentLang]?.copyBtn || 'Copy'}">
            <i class="fa-regular fa-copy"></i>
        </button>
    </div>
    <pre><code class="language-${lang}">${code.trim()}</code></pre>
</div>`;
        codeBlocks.push(formattedCode);
        return placeholder;
    });

    // 3. Extract inline code blocks to protect them
    const inlineCodes = [];
    html = html.replace(/`([^`\n]+)`/g, (match, code) => {
        const placeholder = `<!--__INLINE_CODE_${inlineCodes.length}__-->`;
        inlineCodes.push(`<code>${code}</code>`);
        return placeholder;
    });

    // 4. Format tables
    let lines = html.split('\n');
    let inTable = false;
    let tableHtml = '';
    let newLines = [];
    
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i].trim();
        if (line.startsWith('|') && line.endsWith('|')) {
            if (!inTable) {
                inTable = true;
                tableHtml = '<div class="table-responsive"><table>\n';
                let cells = line.split('|').slice(1, -1);
                tableHtml += '<thead><tr>';
                cells.forEach(c => tableHtml += `<th>${c.trim()}</th>`);
                tableHtml += '</tr></thead>\n<tbody>\n';
            } else {
                if (line.match(/^\|[\s-:]+\|/)) continue;
                let cells = line.split('|').slice(1, -1);
                tableHtml += '<tr>';
                cells.forEach(c => tableHtml += `<td>${c.trim()}</td>`);
                tableHtml += '</tr>\n';
            }
        } else {
            if (inTable) {
                inTable = false;
                tableHtml += '</tbody></table></div>\n';
                newLines.push(tableHtml);
            }
            newLines.push(line);
        }
    }
    if (inTable) {
        tableHtml += '</tbody></table></div>\n';
        newLines.push(tableHtml);
    }
    html = newLines.join('\n');

    // 5. Format Headers
    html = html.replace(/^### (.*$)/gim, "<h3>$1</h3>");
    html = html.replace(/^## (.*$)/gim, "<h2>$1</h2>");
    html = html.replace(/^# (.*$)/gim, "<h1>$1</h1>");
    
    // 6. Format Bold
    html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    
    // 7. Format Lists
    html = html.replace(/^\s*-\s+(.*$)/gim, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>)/gim, "<ul>$1</ul>");
    html = html.replace(/<\/ul>\s*<ul>/g, ""); // Clean consecutive ul tags

    // 8. Format paragraphs (replace double newlines with br, and single newlines with br for clean layout)
    html = html.replace(/\n\n/g, "<br><br>");
    html = html.replace(/\n/g, "<br>");

    // 9. Restore protected blocks
    inlineCodes.forEach((val, idx) => {
        html = html.replace(`<!--__INLINE_CODE_${idx}__-->`, val);
    });
    codeBlocks.forEach((val, idx) => {
        html = html.replace(`<!--__CODE_BLOCK_${idx}__-->`, val);
    });

    return html;
}

// Copy to clipboard helper
function copyText(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Use innerText to copy text without html tags
    const textToCopy = container.innerText;
    
    navigator.clipboard.writeText(textToCopy)
        .then(() => {
            // Find copy button and show feedback
            const btn = container.previousElementSibling?.querySelector(".btn-copy");
            if (btn) {
                const originalHTML = btn.innerHTML;
                btn.innerHTML = `<i class="fa-solid fa-check"></i> ${translations[currentLang].copied}`;
                setTimeout(() => btn.innerHTML = originalHTML, 2000);
            }
        })
        .catch(err => {
            console.error("Clipboard copy failed:", err);
        });
}

// Copy code block helper
window.copyCodeBlock = function(button) {
    const wrapper = button.closest('.code-block-wrapper');
    const codeEl = wrapper.querySelector('code');
    if (!codeEl) return;
    
    navigator.clipboard.writeText(codeEl.innerText)
        .then(() => {
            const originalHTML = button.innerHTML;
            button.innerHTML = `<i class="fa-solid fa-check"></i>`;
            setTimeout(() => button.innerHTML = originalHTML, 2000);
        })
        .catch(err => {
            console.error("Clipboard copy failed:", err);
        });
};

// Custom Modal Alerts
function showAlert(title, message) {
    const modalTitle = document.getElementById("modal-title");
    const modalMessage = document.getElementById("modal-message");
    const modalCancelBtn = document.getElementById("modal-cancel-btn");
    const modal = document.getElementById("modal");
    
    if (modalTitle) modalTitle.textContent = title;
    if (modalMessage) modalMessage.textContent = message;
    
    if (modalCancelBtn) modalCancelBtn.style.display = "none";
    
    modalConfirmCallback = null;
    modalCancelCallback = null;
    if (modal) modal.classList.remove("hidden");
}

function showConfirmAlert(title, message, onConfirm, onCancel) {
    const modalTitle = document.getElementById("modal-title");
    const modalMessage = document.getElementById("modal-message");
    const modalCancelBtn = document.getElementById("modal-cancel-btn");
    const modal = document.getElementById("modal");
    
    if (modalTitle) modalTitle.textContent = title;
    if (modalMessage) modalMessage.textContent = message;
    
    if (modalCancelBtn) modalCancelBtn.style.display = "block";
    
    modalConfirmCallback = onConfirm;
    modalCancelCallback = onCancel;
    if (modal) modal.classList.remove("hidden");
}

function hideModal() {
    const modal = document.getElementById("modal");
    if (modal) modal.classList.add("hidden");
}

function handleFileSelection(e) {
    const files = Array.from(e.target.files);
    if (!files.length) return;
    
    const maxSizeBytes = 15 * 1024 * 1024; // 15MB
    
    files.forEach(file => {
        if (file.size > maxSizeBytes) {
            showAlert(translations[currentLang].alertError || "Error", 
                      (translations[currentLang].fileSizeError || "File too large") + `: ${file.name}`);
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(evt) {
            const fileData = {
                name: file.name,
                mime_type: file.type || "application/octet-stream",
                data: evt.target.result // base64 data url
            };
            
            selectedFiles.push(fileData);
            renderFilePreviews();
        };
        reader.readAsDataURL(file);
    });
    
    fileInput.value = "";
}

function renderFilePreviews() {
    if (!filePreviewContainer) return;
    
    if (selectedFiles.length === 0) {
        filePreviewContainer.classList.add("hidden");
        filePreviewContainer.innerHTML = "";
        return;
    }
    
    filePreviewContainer.classList.remove("hidden");
    filePreviewContainer.innerHTML = "";
    
    selectedFiles.forEach((file, index) => {
        const previewItem = document.createElement("div");
        previewItem.className = "preview-item";
        
        const isImage = file.mime_type.startsWith("image/");
        
        const iconWrapper = document.createElement("div");
        iconWrapper.className = "preview-icon-wrapper";
        
        if (isImage) {
            const img = document.createElement("img");
            img.src = file.data;
            img.alt = file.name;
            img.className = "preview-img";
            iconWrapper.appendChild(img);
        } else {
            const icon = document.createElement("i");
            if (file.mime_type.includes("pdf")) {
                icon.className = "fa-solid fa-file-pdf text-red";
            } else if (file.mime_type.includes("word") || file.mime_type.includes("officedocument.wordprocessing")) {
                icon.className = "fa-solid fa-file-word text-blue";
            } else if (file.mime_type.includes("excel") || file.mime_type.includes("officedocument.spreadsheetml")) {
                icon.className = "fa-solid fa-file-excel text-green";
            } else if (file.mime_type.includes("powerpoint") || file.mime_type.includes("officedocument.presentation")) {
                icon.className = "fa-solid fa-file-powerpoint text-orange";
            } else if (file.mime_type.startsWith("text/")) {
                icon.className = "fa-solid fa-file-lines text-gray";
            } else {
                icon.className = "fa-solid fa-file text-gray";
            }
            iconWrapper.appendChild(icon);
        }
        
        const infoDiv = document.createElement("div");
        infoDiv.className = "preview-info";
        
        const nameSpan = document.createElement("span");
        nameSpan.className = "preview-name";
        nameSpan.textContent = file.name;
        nameSpan.title = file.name;
        
        infoDiv.appendChild(nameSpan);
        
        const removeBtn = document.createElement("button");
        removeBtn.className = "preview-remove-btn";
        removeBtn.innerHTML = "&times;";
        removeBtn.title = "Remove";
        removeBtn.onclick = (e) => {
            e.stopPropagation();
            selectedFiles.splice(index, 1);
            renderFilePreviews();
        };
        previewItem.appendChild(iconWrapper);
        previewItem.appendChild(infoDiv);
        previewItem.appendChild(removeBtn);
        
        filePreviewContainer.appendChild(previewItem);
    });
}



function setMode(mode) {
    activeMode = mode;
    const modeInstantBtn = document.getElementById("mode-instant-btn");
    const modeExpertBtn = document.getElementById("mode-expert-btn");
    const instantAssistants = document.getElementById("instant-assistants");
    const aiToggles = document.querySelector(".ai-toggles");
    const welcomeTitleSpan = document.getElementById("welcome-text-span");
    
    if (mode === "instant") {
        if (modeInstantBtn) modeInstantBtn.classList.add("active");
        if (modeExpertBtn) modeExpertBtn.classList.remove("active");
        if (instantAssistants) instantAssistants.classList.remove("hidden");
        if (aiToggles) aiToggles.classList.add("hidden");
        if (welcomeTitleSpan) {
            welcomeTitleSpan.setAttribute("data-i18n", "welcomeInstant");
            if (translations[currentLang] && translations[currentLang].welcomeInstant) {
                welcomeTitleSpan.textContent = translations[currentLang].welcomeInstant;
            }
        }
    } else {
        if (modeInstantBtn) modeInstantBtn.classList.remove("active");
        if (modeExpertBtn) modeExpertBtn.classList.add("active");
        if (instantAssistants) instantAssistants.classList.add("hidden");
        if (aiToggles) aiToggles.classList.remove("hidden");
        if (welcomeTitleSpan) {
            welcomeTitleSpan.setAttribute("data-i18n", "welcomeExpert");
            if (translations[currentLang] && translations[currentLang].welcomeExpert) {
                welcomeTitleSpan.textContent = translations[currentLang].welcomeExpert;
            }
        }
    }
    updatePromptPlaceholder();
    updateModeBubble();
}

function updateModeBubble() {
    const activeBtn = document.querySelector(".btn-mode.active");
    const container = document.querySelector(".mode-switcher-container");
    const bubble = document.getElementById("mode-bubble");
    if (!activeBtn || !container || !bubble) return;

    const activeRect = activeBtn.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();

    // Calculate left offset relative to the switcher container
    const leftOffset = activeRect.left - containerRect.left;
    const width = activeRect.width;

    // Apply translation relative to container padding (5px)
    bubble.style.transform = `translateX(${leftOffset - 5}px)`;
    bubble.style.width = `${width}px`;

    // Apply correct theme classes to the bubble
    if (activeBtn.id === "mode-instant-btn") {
        bubble.classList.add("instant");
        bubble.classList.remove("expert");
    } else {
        bubble.classList.add("expert");
        bubble.classList.remove("instant");
    }
}

function updatePromptPlaceholder() {
    const textarea = document.getElementById("prompt-textarea");
    if (!textarea) return;
    
    if (activeMode === "instant") {
        const key = `promptPlaceholder${activeInstantAssistant.charAt(0).toUpperCase() + activeInstantAssistant.slice(1)}`;
        textarea.setAttribute("data-i18n-placeholder", key);
        if (translations[currentLang] && translations[currentLang][key]) {
            textarea.setAttribute("placeholder", translations[currentLang][key]);
        }
    } else {
        textarea.setAttribute("data-i18n-placeholder", "promptPlaceholder");
        if (translations[currentLang] && translations[currentLang].promptPlaceholder) {
            textarea.setAttribute("placeholder", translations[currentLang].promptPlaceholder);
        }
    }
}

async function handleNewChat() {
    const promptTextarea = document.getElementById("prompt-textarea");
    if (promptTextarea) {
        promptTextarea.value = "";
        promptTextarea.focus();
    }
    currentSessionId = Date.now().toString();
    renderActiveSession();
    renderSidebarHistory(chatHistory);
    
    // Silently reset browser tabs
    try {
        await fetch("/api/browser/new_chat", { method: "POST" });
    } catch (e) {
        console.error("Failed to reset browser tabs for new chat:", e);
    }
}

function filterHistoryList(query) {
    const historyItems = document.querySelectorAll(".history-item");
    const groupTitles = document.querySelectorAll(".history-group-title");
    
    historyItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text.includes(query)) {
            item.style.display = "flex";
        } else {
            item.style.display = "none";
        }
    });
    
    groupTitles.forEach(title => {
        if (query) {
            title.style.display = "none";
        } else {
            title.style.display = "block";
        }
    });
}

