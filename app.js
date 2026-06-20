// Global memory state for tracking focus modes
let currentActiveSteps = [];
let focusStepIndex = 0;

document.getElementById('recipeForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    // Grab the live inputs from our UI elements
    const videoUrl = document.getElementById('videoUrl').value;
    const chosenLanguage = document.getElementById('language').value;
    
    const loadingSection = document.getElementById('loadingStatus');
    const resultsSection = document.getElementById('recipeResult');
    
    // Show the liquid glass loader animation fluidly
    loadingSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    
    let fetchedTitle = "Cooking Recipe Video Stream";

    // BROWSER-SIDE FETCH: Get the real YouTube video title securely without getting blocked
    try {
        if (videoUrl.includes('youtube.com') || videoUrl.includes('youtu.be')) {
            const oEmbedUrl = `https://www.youtube.com/oembed?url=${encodeURIComponent(videoUrl)}&format=json`;
            const titleResponse = await fetch(oEmbedUrl);
            if (titleResponse.ok) {
                const titleData = await titleResponse.json();
                if (titleData.title) {
                    fetchedTitle = titleData.title;
                }
            }
        }
    } catch (titleError) {
        console.log("Could not fetch title from browser side, falling back:", titleError);
    }
    
    try {
        // Make a real network handshake request to our Django server endpoint
        const response = await fetch('/api/distill/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                url: videoUrl, 
                lang: chosenLanguage,
                video_title: fetchedTitle // <-- Passing the real title we grabbed
            })
        });
        
        if (!response.ok) {
            throw new Error('Network pipeline rejected request');
        }
        
        // Unpack the JSON data package sent back by Django
        const processData = await response.json();
        
        // Save extracted steps globally so Focus Mode can access them
        currentActiveSteps = processData.steps;
        
        document.getElementById('recipeTitle').innerText = processData.title;
        
        // Render Ingredients List dynamically
        const ingredientsUl = document.getElementById('ingredientsList');
        ingredientsUl.innerHTML = ''; 
        processData.ingredients.forEach(item => {
            const li = document.createElement('li');
            li.className = 'bg-white/5 p-3 rounded-xl border border-white/5 flex items-center gap-2';
            li.innerHTML = `<span class="text-emerald-400 font-bold">✓</span> ${item}`;
            ingredientsUl.appendChild(li);
        });
        
        // Render Step Cards dynamically
        const stepsContainer = document.getElementById('stepsContainer');
        stepsContainer.innerHTML = ''; 
        processData.steps.forEach((singleStep, index) => {
            const stepBox = document.createElement('div');
            stepBox.className = 'liquid-glass-panel p-5 flex gap-4 items-start clickable-step';
            stepBox.innerHTML = `
                <div class="step-badge w-8 h-8 rounded-xl flex items-center justify-center font-black text-emerald-400 shrink-0 text-sm">
                    ${index + 1}
                </div>
                <p class="text-sm md:text-base leading-relaxed pt-0.5 text-slate-200">${singleStep}</p>
            `;
            
            // Launch Focus Mode overlay when tapped
            stepBox.addEventListener('click', () => {
                launchFocusMode(index);
            });
            
            stepsContainer.appendChild(stepBox);
        });
        
        // Transition visual layers fluidly
        loadingSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error("Pipeline failure:", error);
        alert("Server failed to communicate. Check terminal logs.");
        loadingSection.classList.add('hidden');
    }
});

// --- Focus Mode Presenter Core Engine ---
function launchFocusMode(index) {
    focusStepIndex = index;
    updateFocusUI();
    document.getElementById('focusOverlay').classList.remove('hidden');
}

function updateFocusUI() {
    document.getElementById('focusBadge').innerText = `STEP ${focusStepIndex + 1}`;
    document.getElementById('focusText').innerText = currentActiveSteps[focusStepIndex];
    document.getElementById('focusIndicator').innerText = `${focusStepIndex + 1} / ${currentActiveSteps.length}`;
    
    document.getElementById('prevStepBtn').disabled = (focusStepIndex === 0);
    document.getElementById('nextStepBtn').disabled = (focusStepIndex === currentActiveSteps.length - 1);
}

// Attach event tracking triggers to Focus Mode navigation panels
document.getElementById('closeFocusBtn').addEventListener('click', () => {
    document.getElementById('focusOverlay').classList.add('hidden');
});

document.getElementById('prevStepBtn').addEventListener('click', () => {
    if (focusStepIndex > 0) {
        focusStepIndex--;
        updateFocusUI();
    }
});

document.getElementById('nextStepBtn').addEventListener('click', () => {
    if (focusStepIndex < currentActiveSteps.length - 1) {
        focusStepIndex++;
        updateFocusUI();
    }
});