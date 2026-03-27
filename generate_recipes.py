import urllib.request
import json
import os
import string
import re

meals = []
for letter in string.ascii_lowercase:
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?f={letter}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data and 'meals' in data and data['meals']:
                meals.extend(data['meals'])
                print(f"Got {len(data['meals'])} meals for {letter}")
    except Exception as e:
        print(f"Error fetching {letter}: {e}")
    
    if len(meals) >= 100:
        break

meals = meals[:100]

recipes = []
for i, meal in enumerate(meals):
    ingredients = []
    for j in range(1, 21):
        ing = meal.get(f"strIngredient{j}")
        measure = meal.get(f"strMeasure{j}")
        if ing and ing.strip():
            measure = measure.strip() if measure else ""
            ingredients.append(f"{measure} {ing}".strip())
    
    instructions = meal.get("strInstructions", "")
    instruction_list = [inst.strip() for inst in instructions.replace('\r\n', '\n').split('\n') if inst.strip()]
    
    category = meal.get("strCategory", "Dinner")
    # map some categories to match UI
    ui_cat = "Dinner"
    if category and category.lower() in ["dessert"]:
        ui_cat = "Dessert"
    elif category and category.lower() in ["vegetarian", "vegan", "breakfast", "starter"]:
        ui_cat = "Healthy"
    
    recipe = {
        "id": i + 1,
        "title": meal.get("strMeal", "Delicious Meal"),
        "description": f"A delightful {meal.get('strArea', 'International')} {category.lower()} dish that is sure to please.",
        "category": ui_cat,
        "time": f"{30 + (i % 30)} mins",
        "difficulty": ["Easy", "Medium", "Hard"][i % 3],
        "servings": 2 + (i % 4),
        "image": meal.get("strMealThumb", ""),
        "ingredients": ingredients,
        "instructions": instruction_list
    }
    recipes.append(recipe)

recipes_json = json.dumps(recipes, indent=4)

js_content = f"""const recipes = {recipes_json};

const recipeGrid = document.getElementById('recipeGrid');
const searchInput = document.getElementById('searchInput');

// Modal Elements
const modal = document.getElementById('recipeModal');
const closeModalBtn = document.getElementById('closeModal');
const modalImage = document.getElementById('modalImage');
const modalTags = document.getElementById('modalTags');
const modalTitle = document.getElementById('modalTitle');
const modalDesc = document.getElementById('modalDesc');
const modalTime = document.getElementById('modalTime');
const modalDifficulty = document.getElementById('modalDifficulty');
const modalServings = document.getElementById('modalServings');
const modalIngredients = document.getElementById('modalIngredients');
const modalInstructions = document.getElementById('modalInstructions');
const filterBtns = document.querySelectorAll('.filter-pills button');

function renderRecipes(filter = "All", search = "") {{
    recipeGrid.innerHTML = "";
    
    let filteredRecipes = recipes.filter(recipe => {{
        const matchesCategory = filter === "All" || recipe.category === filter;
        const matchesSearch = recipe.title.toLowerCase().includes(search.toLowerCase()) || 
                              recipe.ingredients.some(i => i.toLowerCase().includes(search.toLowerCase()));
        return matchesCategory && matchesSearch;
    }});

    if(filteredRecipes.length === 0) {{
        recipeGrid.innerHTML = "<p style='grid-column: 1/-1; text-align: center; color: var(--text-secondary); padding: 2rem;'>No recipes found.</p>";
        return;
    }}

    filteredRecipes.forEach(recipe => {{
        const card = document.createElement('div');
        card.classList.add('recipe-card');
        card.innerHTML = `
            <div class="card-img">
                <img src="${{recipe.image}}" alt="${{recipe.title}}">
            </div>
            <div class="card-content">
                <span class="card-tag">${{recipe.category}}</span>
                <h3 class="card-title">${{recipe.title}}</h3>
                <p class="card-desc">${{recipe.description}}</p>
                <div class="card-meta">
                    <span><i class="fa-regular fa-clock"></i> ${{recipe.time}}</span>
                    <span><i class="fa-solid fa-chart-simple"></i> ${{recipe.difficulty}}</span>
                </div>
            </div>
        `;
        card.addEventListener('click', () => openModal(recipe));
        recipeGrid.appendChild(card);
    }});
}}

function openModal(recipe) {{
    modalImage.src = recipe.image;
    modalTags.innerHTML = `<span>${{recipe.category}}</span>`;
    modalTitle.textContent = recipe.title;
    modalDesc.textContent = recipe.description;
    
    modalTime.innerHTML = `<i class="fa-regular fa-clock"></i> ${{recipe.time}}`;
    modalDifficulty.innerHTML = `<i class="fa-solid fa-chart-simple"></i> ${{recipe.difficulty}}`;
    modalServings.innerHTML = `<i class="fa-solid fa-user-group"></i> ${{recipe.servings}} Servings`;

    // Populate Ingredients
    modalIngredients.innerHTML = recipe.ingredients.map(ing => {{
        let parts = ing.split(" ");
        let highlight = parts.shift();
        return `<li><span><strong>${{highlight}}</strong> ${{parts.join(" ")}}</span> <i class="fa-solid fa-check" style="color:var(--text-secondary); opacity:0.3"></i></li>`;
    }}).join("");

    // Populate Instructions
    modalInstructions.innerHTML = recipe.instructions.map(inst => `<li>${{inst}}</li>`).join("");

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}}

function closeModal() {{
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}}

// Event Listeners
searchInput.addEventListener('input', (e) => {{
    const activeFilter = document.querySelector('.filter-pills button.active').textContent;
    renderRecipes(activeFilter, e.target.value);
}});

filterBtns.forEach(btn => {{
    btn.addEventListener('click', () => {{
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderRecipes(btn.textContent, searchInput.value);
    }});
}});

closeModalBtn.addEventListener('click', closeModal);
modal.addEventListener('click', (e) => {{
    if(e.target === modal) closeModal();
}});

// Init
renderRecipes();
"""

with open("script.js", "w", encoding='utf-8') as f:
    f.write(js_content)

print(f"Successfully wrote {len(recipes)} recipes to script.js")
