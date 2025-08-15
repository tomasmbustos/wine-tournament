const API_BASE = '/api/v1/tournament';
let currentParticipant = null;
let allParticipants = [];

// Navigation
function showSection(sectionId, event = null) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionId).classList.add('active');
    
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Only try to set active button if event is provided
    if (event && event.target) {
        event.target.classList.add('active');
    } else {
        // Fallback: find the correct button based on section
        const targetButton = Array.from(document.querySelectorAll('.nav-btn')).find(btn => {
            return btn.textContent.toLowerCase() === sectionId.toLowerCase() || 
                   (sectionId === 'participants' && btn.textContent === 'Participants') ||
                   (sectionId === 'voting' && btn.textContent === 'Votes');
        });
        if (targetButton) {
            targetButton.classList.add('active');
        }
    }

    // Load data when switching to certain sections
    if (sectionId === 'participants') {
        loadParticipants();
        loadWineCapacity();
    } else if (sectionId === 'voting') {
        loadParticipantsForVoting();
        loadLeaderboard();
        updateVotingProgress();
    }
}

// Participant Registration
document.getElementById('participant-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('participant-name').value;
    const totalWines = parseInt(document.getElementById('total-wines').value);
    
    try {
        const response = await fetch(`${API_BASE}/participants/suggest?total_wines=${totalWines}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentParticipant = data.participant;
            showWineAssignment(data.participant.name, data.suggestedWines);
        } else {
            showResult('Error generating wine assignment: ' + data.detail, 'error');
        }
    } catch (error) {
        showResult('Error: ' + error.message, 'error');
    }
});

function showWineAssignment(name, wines) {
    document.getElementById('assigned-participant-name').textContent = name;
    document.getElementById('wine-assignment').style.display = 'block';
    
    // Start the casino slot machine animation
    startSlotMachine(wines);
}

function startSlotMachine(finalWines) {
    const slots = document.querySelectorAll('.slot');
    const inputs = document.querySelectorAll('.slot-input');
    const totalWines = parseInt(document.getElementById('total-wines').value) || 20;
    
    // Show/hide slots based on number of wines available
    slots.forEach((slot, index) => {
        if (index < finalWines.length) {
            slot.style.display = 'block';
            slot.classList.add('spinning');
        } else {
            slot.style.display = 'none';
        }
    });
    
    // Update help text if fewer than 5 wines
    const helpText = document.querySelector('.casino-help');
    if (finalWines.length < 5) {
        helpText.innerHTML = `⚠️ Tournament is nearly full! Only ${finalWines.length} wines have available spots. These numbers are pre-selected to respect wine limits.`;
        helpText.style.background = '#FEF3C7';
        helpText.style.borderLeftColor = '#F59E0B';
    }
    
    // Randomly change numbers during spinning (just for visual effect)
    const visibleInputs = Array.from(inputs).slice(0, finalWines.length);
    const spinInterval = setInterval(() => {
        visibleInputs.forEach(input => {
            input.value = Math.floor(Math.random() * totalWines) + 1;
        });
    }, 50);
    
    // Stop slots one by one with dramatic timing
    finalWines.forEach((wine, index) => {
        setTimeout(() => {
            // Stop the spinning interval when we start revealing the first slot
            if (index === 0) {
                clearInterval(spinInterval);
            }
            
            // Get the actual slot and input elements by their position in visible slots
            const slot = slots[index];
            const input = inputs[index];
            
            if (!slot || !input) {
                console.error(`Slot or input not found at index ${index}`);
                return;
            }
            
            // Stop spinning this slot
            slot.classList.remove('spinning');
            slot.classList.add('revealing');
            
            // Set final value
            input.value = wine;
            
            // Remove reveal animation after it completes
            setTimeout(() => {
                slot.classList.remove('revealing');
            }, 500);
        }, 1000 + (index * 300)); // Stagger the reveals
    });
    
    // Add input validation after animation completes
    setTimeout(() => {
        addSlotValidation();
    }, 1000 + (finalWines.length * 300) + 500);
}

function addSlotValidation() {
    const slotInputs = document.querySelectorAll('.slot-input');
    slotInputs.forEach(input => {
        input.addEventListener('input', validateSlotInput);
        input.addEventListener('blur', validateSlotInput);
    });
}

function validateSlotInput(event) {
    const input = event.target;
    const value = parseInt(input.value);
    const totalWines = parseInt(document.getElementById('total-wines').value) || 20;
    
    // Reset styles
    input.style.borderColor = '';
    input.style.backgroundColor = '';
    
    if (isNaN(value) || value < 1 || value > totalWines) {
        input.style.borderColor = '#DC2626';
        input.style.backgroundColor = '#FEF2F2';
        return;
    }
    
    // Check for duplicates
    const allInputs = document.querySelectorAll('.slot-input');
    const values = Array.from(allInputs).map(inp => parseInt(inp.value)).filter(v => !isNaN(v));
    const duplicates = values.filter((v, i) => values.indexOf(v) !== i);
    
    if (duplicates.includes(value)) {
        input.style.borderColor = '#F59E0B';
        input.style.backgroundColor = '#FEF3C7';
    }
}

function regenerateWines() {
    const name = currentParticipant.name;
    const totalWines = parseInt(document.getElementById('total-wines').value);
    
    fetch(`${API_BASE}/participants/suggest?total_wines=${totalWines}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name })
    })
    .then(response => response.json())
    .then(data => {
        if (data.participant) {
            currentParticipant = data.participant;
            startSlotMachine(data.suggestedWines);
        }
    })
    .catch(error => {
        showResult('Error regenerating wines: ' + error.message, 'error');
    });
}

async function confirmParticipant() {
    // Get wines from visible slot inputs only
    const slots = document.querySelectorAll('.slot');
    const visibleSlots = Array.from(slots).filter(slot => slot.style.display !== 'none');
    const slotInputs = visibleSlots.map(slot => slot.querySelector('.slot-input'));
    const editedWines = slotInputs.map(input => parseInt(input.value)).filter(w => !isNaN(w));
    
    const expectedWines = visibleSlots.length;
    if (editedWines.length !== expectedWines) {
        showResult(`Please provide exactly ${expectedWines} wine numbers`, 'error');
        return;
    }
    
    // Check for duplicate wines
    const uniqueWines = new Set(editedWines);
    if (uniqueWines.size !== expectedWines) {
        showResult('All wine numbers must be different', 'error');
        return;
    }
    
    currentParticipant.assignedWines = editedWines;
    
    try {
        const response = await fetch(`${API_BASE}/participants/confirm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(currentParticipant)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showResult('Participant added successfully!', 'success');
            document.getElementById('participant-form').reset();
            document.getElementById('wine-assignment').style.display = 'none';
            currentParticipant = null;
            loadParticipants(); // Refresh the participants list
            loadWineCapacity(); // Refresh the wine capacity display
        } else {
            showResult('Error: ' + data.detail, 'error');
        }
    } catch (error) {
        showResult('Error: ' + error.message, 'error');
    }
}

// View Participants
async function loadParticipants() {
    try {
        const response = await fetch(`${API_BASE}/participants`);
        const participants = await response.json();
        
        if (response.ok) {
            displayParticipants(participants);
            allParticipants = participants;
        } else {
            showResult('Error loading participants', 'error');
        }
    } catch (error) {
        showResult('Error: ' + error.message, 'error');
    }
}

function displayParticipants(participants) {
    const container = document.getElementById('participants-list');
    
    // Update total participants subtitle
    document.getElementById('total-participants-subtitle').textContent = `Total participants: ${participants.length}`;
    
    if (participants.length === 0) {
        container.innerHTML = '<p>No participants yet. Add some participants first!</p>';
        return;
    }
    
    // Sort participants alphabetically by name
    const sortedParticipants = participants.sort((a, b) => 
        a.name.toLowerCase().localeCompare(b.name.toLowerCase())
    );
    
    const list = document.createElement('div');
    list.className = 'participants-simple-list';
    
    sortedParticipants.forEach(participant => {
        const item = document.createElement('div');
        item.className = 'participant-item';
        
        const wineNumbers = participant.assignedWines.map(wine => 
            `<span class="wine-number">${wine}</span>`
        ).join('');
        
        item.innerHTML = `
            <span class="participant-name">${participant.name}</span>
            <div class="wine-list">${wineNumbers}</div>
        `;
        
        list.appendChild(item);
    });
    
    container.innerHTML = '';
    container.appendChild(list);
}

// Voting
async function loadParticipantsForVoting() {
    try {
        const response = await fetch(`${API_BASE}/participants`);
        const participants = await response.json();
        
        if (response.ok) {
            const select = document.getElementById('vote-participant');
            select.innerHTML = '<option value="">Choose participant...</option>';
            
            // Sort participants alphabetically by name
            const sortedParticipants = participants.sort((a, b) => 
                a.name.toLowerCase().localeCompare(b.name.toLowerCase())
            );
            
            sortedParticipants.forEach(participant => {
                const option = document.createElement('option');
                option.value = participant.id;
                option.textContent = participant.name;
                option.dataset.wines = JSON.stringify(participant.assignedWines);
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading participants for voting:', error);
    }
}

document.getElementById('vote-participant').addEventListener('change', (e) => {
    const selectedOption = e.target.selectedOptions[0];
    const wineRanking = document.getElementById('wine-ranking');
    
    if (selectedOption.value) {
        const wines = JSON.parse(selectedOption.dataset.wines);
        populateWineSelects(wines);
        wineRanking.style.display = 'block';
    } else {
        wineRanking.style.display = 'none';
    }
});

function populateWineSelects(wines) {
    const selects = ['first-place', 'second-place', 'third-place'];
    
    // Handle case where participant has fewer than 3 wines
    if (wines.length < 3) {
        showResult(`This participant has only ${wines.length} wines. Cannot vote (need at least 3 wines for 1st, 2nd, 3rd place).`, 'error');
        return;
    }
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Choose wine...</option>';
        
        wines.forEach(wine => {
            const option = document.createElement('option');
            option.value = wine;
            option.textContent = `Wine ${wine}`;
            select.appendChild(option);
        });
        
        // Add change listener to prevent same wine selection
        select.addEventListener('change', validateWineSelection);
    });
}

function validateWineSelection() {
    const first = document.getElementById('first-place').value;
    const second = document.getElementById('second-place').value;
    const third = document.getElementById('third-place').value;
    
    const selected = [first, second, third].filter(v => v);
    const unique = new Set(selected);
    
    if (selected.length !== unique.size) {
        showResult('Each wine can only be selected once!', 'error');
        return false;
    }
    
    return true;
}

document.getElementById('vote-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!validateWineSelection()) {
        return;
    }
    
    const participantId = document.getElementById('vote-participant').value;
    const firstPlace = parseInt(document.getElementById('first-place').value);
    const secondPlace = parseInt(document.getElementById('second-place').value);
    const thirdPlace = parseInt(document.getElementById('third-place').value);
    
    if (!participantId || !firstPlace || !secondPlace || !thirdPlace) {
        showResult('Please fill all fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/votes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                participantId,
                firstPlace,
                secondPlace,
                thirdPlace
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showResult('Vote submitted successfully!', 'success');
            document.getElementById('vote-form').reset();
            document.getElementById('wine-ranking').style.display = 'none';
            loadLeaderboard();
            updateVotingProgress();
        } else {
            showResult('Error: ' + data.detail, 'error');
        }
    } catch (error) {
        showResult('Error: ' + error.message, 'error');
    }
});

// Leaderboard
async function loadLeaderboard() {
    try {
        const response = await fetch(`${API_BASE}/leaderboard`);
        const leaderboard = await response.json();
        
        if (response.ok) {
            displayLeaderboard(leaderboard);
        } else {
            document.getElementById('leaderboard-list').innerHTML = '<p>Error loading leaderboard</p>';
        }
    } catch (error) {
        document.getElementById('leaderboard-list').innerHTML = '<p>Error loading leaderboard</p>';
    }
}

function displayLeaderboard(leaderboard) {
    const container = document.getElementById('leaderboard-list');
    
    if (leaderboard.length === 0) {
        container.innerHTML = '<p>No votes yet. Submit some votes to see the leaderboard!</p>';
        return;
    }
    
    const list = document.createElement('div');
    
    leaderboard.forEach((wine, index) => {
        const item = document.createElement('div');
        item.className = 'leaderboard-item';
        
        if (index === 0) item.classList.add('first');
        else if (index === 1) item.classList.add('second');
        else if (index === 2) item.classList.add('third');
        
        const rank = index + 1;
        const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : `${rank}.`;
        
        item.innerHTML = `
            <span>${medal} <span class="wine-id">Wine ${wine.wineId}</span></span>
            <span class="points">${wine.totalPoints} pts</span>
        `;
        
        // Add entrance animation with stagger
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            item.style.transition = 'all 0.5s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, index * 100);
        
        list.appendChild(item);
    });
    
    container.innerHTML = '';
    container.appendChild(list);
}

async function updateVotingProgress() {
    try {
        const response = await fetch(`${API_BASE}/voting-stats`);
        const votingStats = await response.json();
        
        if (response.ok) {
            // Update stats
            document.getElementById('total-votes-progress').textContent = votingStats.total_votes;
            document.getElementById('voting-percentage').textContent = `${votingStats.voting_percentage}%`;
            
            // Update progress bar with animation
            const progressBar = document.getElementById('progress-bar');
            progressBar.style.width = `${votingStats.voting_percentage}%`;
            
            // Update participant pills
            updateParticipantPills(votingStats.participant_status);
            
            // Check if voting is complete (100%)
            if (votingStats.voting_percentage >= 100) {
                // Small delay to let the progress bar animation complete
                setTimeout(() => {
                    showCelebration();
                }, 1000);
            }
        }
    } catch (error) {
        console.error('Error updating voting progress:', error);
    }
}

function updateParticipantPills(participantStatus) {
    const container = document.getElementById('participant-pills');
    container.innerHTML = '';
    
    if (participantStatus.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No participants yet</p>';
        return;
    }
    
    participantStatus.forEach((participant, index) => {
        const pill = document.createElement('div');
        pill.className = 'participant-pill';
        
        // Mark as voted if participant has submitted a vote
        if (participant.has_voted) {
            pill.classList.add('voted');
        }
        
        pill.textContent = participant.name;
        
        // Add entrance animation
        pill.style.opacity = '0';
        pill.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
            pill.style.transition = 'all 0.3s ease';
            pill.style.opacity = '1';
            pill.style.transform = 'translateY(0)';
        }, index * 50);
        
        container.appendChild(pill);
    });
}

// Utility function for showing results
function showResult(message, type) {
    const resultDiv = document.getElementById('participant-result');
    resultDiv.textContent = message;
    resultDiv.className = `result-message ${type}`;
    resultDiv.style.display = 'block';
    
    setTimeout(() => {
        resultDiv.style.display = 'none';
    }, 5000);
}

// Wine Capacity Visualization
async function loadWineCapacity() {
    try {
        const response = await fetch(`${API_BASE}/participants`);
        const participants = await response.json();
        
        if (response.ok) {
            displayWineCapacity(participants);
        } else {
            document.getElementById('wine-capacity-list').innerHTML = '<p>Error loading wine capacity</p>';
        }
    } catch (error) {
        document.getElementById('wine-capacity-list').innerHTML = '<p>Error loading wine capacity</p>';
    }
}

function displayWineCapacity(participants) {
    const totalWines = parseInt(document.getElementById('total-wines').value) || 20;
    const maxParticipants = 5;
    
    // Update total wines subtitle
    document.getElementById('total-wines-subtitle').textContent = `Total wines: ${totalWines}`;
    
    // Count participants per wine
    const wineCounts = {};
    participants.forEach(participant => {
        participant.assignedWines.forEach(wine => {
            wineCounts[wine] = (wineCounts[wine] || 0) + 1;
        });
    });
    
    const container = document.getElementById('wine-capacity-list');
    const list = document.createElement('div');
    
    // Generate display for wines 1 to totalWines
    for (let wineId = 1; wineId <= totalWines; wineId++) {
        const count = wineCounts[wineId] || 0;
        const percentage = (count / maxParticipants) * 100;
        
        const item = document.createElement('div');
        item.className = 'wine-capacity-item';
        
        // Determine color class based on capacity
        let colorClass = 'low';
        if (count >= maxParticipants) colorClass = 'full';
        else if (count >= 4) colorClass = 'high';
        else if (count >= 2) colorClass = 'medium';
        
        item.innerHTML = `
            <div class="wine-info">
                <span class="wine-label">Wine ${wineId}</span>
                <span class="wine-count">${count}/${maxParticipants}</span>
            </div>
            <div class="capacity-bar-container">
                <div class="capacity-bar ${colorClass}" style="width: ${percentage}%"></div>
            </div>
            <span class="capacity-percentage">${Math.round(percentage)}%</span>
        `;
        
        list.appendChild(item);
    }
    
    container.innerHTML = '';
    container.appendChild(list);
}

// Celebration Functions
async function showCelebration() {
    try {
        // Get the final leaderboard for the podium
        const response = await fetch(`${API_BASE}/leaderboard`);
        const leaderboard = await response.json();
        
        if (response.ok && leaderboard.length >= 3) {
            createCelebrationModal(leaderboard);
        }
    } catch (error) {
        console.error('Error loading leaderboard for celebration:', error);
    }
}

function createCelebrationModal(leaderboard) {
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'celebration-overlay';
    
    // Create content container
    const content = document.createElement('div');
    content.className = 'celebration-content';
    
    // Add confetti
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.animationDelay = Math.random() * 3 + 's';
        confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
        content.appendChild(confetti);
    }
    
    // Create celebration content
    content.innerHTML += `
        <h1 class="celebration-title">🏆 Tournament Complete! 🏆</h1>
        <div class="podium-container">
            <!-- Second Place -->
            <div class="podium-place podium-second">
                <div class="podium-wine">🥈 Wine ${leaderboard[1].wineId}</div>
                <div class="podium-base">2</div>
            </div>
            
            <!-- First Place -->
            <div class="podium-place podium-first">
                <div class="podium-wine">🥇 Wine ${leaderboard[0].wineId}</div>
                <div class="podium-base">1</div>
            </div>
            
            <!-- Third Place -->
            <div class="podium-place podium-third">
                <div class="podium-wine">🥉 Wine ${leaderboard[2].wineId}</div>
                <div class="podium-base">3</div>
            </div>
        </div>
        <p style="color: var(--text-secondary); font-size: 1.1rem; margin: var(--space-lg) 0;">
            🎉 Congratulations to all participants! 🎉
        </p>
        <button class="celebration-close" onclick="closeCelebration()">Continue to Results</button>
    `;
    
    overlay.appendChild(content);
    document.body.appendChild(overlay);
    
    // Trigger animations
    setTimeout(() => {
        overlay.classList.add('showing');
        content.classList.add('showing');
    }, 100);
    
    // Store reference for closing
    window.currentCelebration = overlay;
}

function closeCelebration() {
    if (window.currentCelebration) {
        // Fade out animation
        window.currentCelebration.style.opacity = '0';
        window.currentCelebration.style.transform = 'scale(0.95)';
        
        setTimeout(() => {
            document.body.removeChild(window.currentCelebration);
            window.currentCelebration = null;
        }, 300);
    }
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    showSection('participants');
});