const BASE_API_URL = "http://127.0.0.1:8000/api/v1";
const API_KEY = "change-moi";   // la même valeur que API_KEY dans .env

/**
 * Fonction globale pour masquer les alertes d'erreurs.
 */
function hideError() {
    const alertEl = document.getElementById("alert-error");
    alertEl.classList.add("hidden");
}

/**
 * Fonction pour afficher une erreur stylisée dans le panel d'alerte.
 */
function showError(message) {
    const alertEl = document.getElementById("alert-error");
    const msgEl = document.getElementById("alert-error-msg");
    msgEl.textContent = message;
    alertEl.classList.remove("hidden");
}

/**
 * ÉTAPE 1 : Recherche du produit sur l'API OpenFoodFacts (DuckDB Parquet)
 */
async function searchProduct() {
    const barcodeInput = document.getElementById("barcode");
    const barcode = barcodeInput.value.trim();

    // Réinitialisation de l'interface
    hideError();
    const productCard = document.getElementById("product-card");
    productCard.classList.add("hidden", "scale-95", "opacity-0");

    if (!barcode) {
        showError("Veuillez saisir un code-barres valide (ex: 3017620422003).");
        return;
    }

    // Bouton de chargement (Spinner UI)
    const btnSearch = document.getElementById("btn-search");
    const searchSpinner = document.getElementById("search-spinner");
    const searchBtnText = document.getElementById("search-btn-text");

    btnSearch.disabled = true;
    searchSpinner.classList.remove("hidden");
    searchBtnText.textContent = "Recherche...";

    try {
        const response = await fetch(`${BASE_API_URL}/products/${barcode}`, {
            headers: {
                "X-API-KEY": API_KEY
            }
        });
        
        if (response.status === 404) {
            showError("Produit introuvable dans le dataset OpenFoodFacts France.");
            return;
        }

        if (!response.ok) {
            throw new Error(`Erreur serveur (${response.status})`);
        }

        const product = await response.json();

        // Remplissage de la carte produit
        document.getElementById("product-name").textContent = product.product_name || "Produit sans nom";
        document.getElementById("product-barcode").textContent = `Code: ${product.code}`;
        document.getElementById("product-calories").textContent = product.energy_kcal_100g.toFixed(1);

        // Pré-remplissage automatique des calories pour l'Étape 2
        const caloriesInput = document.getElementById("calories-100g");
        caloriesInput.value = product.energy_kcal_100g.toFixed(1);
        
        // Animation d'apparition de la carte produit
        productCard.classList.remove("hidden");
        setTimeout(() => {
            productCard.classList.remove("scale-95", "opacity-0");
            productCard.classList.add("scale-100", "opacity-100");
        }, 50);

    } catch (err) {
        showError(`Impossible de contacter l'API de recherche : ${err.message}`);
    } finally {
        // Rétablir le bouton
        btnSearch.disabled = false;
        searchSpinner.classList.add("hidden");
        searchBtnText.textContent = "Chercher";
    }
}

/**
 * ÉTAPE 2 : Inférence via le modèle de Machine Learning FastAPI
 */
async function predictWeight() {
    hideError();

    const userBmrVal = document.getElementById("user-bmr").value;
    const portionGVal = document.getElementById("portion-g").value;
    const calories100gVal = document.getElementById("calories-100g").value;

    if (!userBmrVal || !portionGVal || !calories100gVal) {
        showError("Veuillez remplir tous les champs de l'étape 2 (BMR, Portion, et Calories).");
        return;
    }

    const payload = {
        user_bmr: parseFloat(userBmrVal),
        portion_g: parseFloat(portionGVal),
        biscuit_calories_100g: parseFloat(calories100gVal)
    };

    // Bouton de chargement (Spinner UI)
    const btnPredict = document.getElementById("btn-predict");
    const predictSpinner = document.getElementById("predict-spinner");
    const predictBtnText = document.getElementById("predict-btn-text");
    const resultCard = document.getElementById("result-card");

    btnPredict.disabled = true;
    predictSpinner.classList.remove("hidden");
    predictBtnText.textContent = "Inférence en cours...";
    resultCard.classList.add("scale-95", "opacity-0");

    try {
        const response = await fetch(`${BASE_API_URL}/predict`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-API-KEY": API_KEY
            },
            body: JSON.stringify(payload)
        });

        // Gestion d'erreur Pydantic (422)
        if (response.status === 422) {
            const errData = await response.json();
            // Formater un message d'erreur lisible à partir du tableau FastAPI detail
            const details = errData.detail.map(d => {
                const fieldName = d.loc[d.loc.length - 1];
                return `${fieldName} : ${d.msg}`;
            }).join(" | ");
            showError(`Données invalides : ${details}`);
            resultCard.classList.add("hidden");
            return;
        }

        if (!response.ok) {
            const errBody = await response.json().catch(() => ({}));
            throw new Error(errBody.detail || `Erreur serveur (${response.status})`);
        }

        const data = await response.json();
        const delta = data.predicted_weight_delta_grams;

        // Mise à jour de l'affichage du résultat
        const resultTitle = document.getElementById("result-title");
        const resultDesc = document.getElementById("result-desc");
        const resultValue = document.getElementById("result-value");
        const resultGlow = document.getElementById("result-glow");

        // Formatage de la valeur de sortie
        resultValue.textContent = (delta >= 0 ? "+" : "") + delta.toFixed(2);

        // Réinitialisation des classes dynamiques de couleur
        resultCard.className = "rounded-2xl p-6 border shadow-2xl relative overflow-hidden transition-all duration-500";
        resultGlow.className = "absolute -bottom-16 -left-16 w-32 h-32 rounded-full blur-2xl";

        if (delta > 0) {
            // Prise de poids : Style Rouge/Rose Corail
            resultCard.classList.add("bg-rose-500/10", "border-rose-500/20", "text-rose-400");
            resultGlow.classList.add("bg-rose-500/15");
            resultTitle.textContent = "Prise de Poids Estimée (Excédent)";
            resultDesc.textContent = "Cette consommation génère un excédent calorique supérieur à votre métabolisme de base.";
        } else if (delta < 0) {
            // Perte de poids : Style Vert Émeraude
            resultCard.classList.add("bg-emerald-500/10", "border-emerald-500/20", "text-emerald-400");
            resultGlow.classList.add("bg-emerald-500/15");
            resultTitle.textContent = "Perte de Poids Estimée (Déficit)";
            resultDesc.textContent = "Le métabolisme de base compense l'apport de cette portion. Balance globale déficitaire.";
        } else {
            // Équilibre : Style Indigo/Bleu
            resultCard.classList.add("bg-indigo-500/10", "border-indigo-500/20", "text-indigo-400");
            resultGlow.classList.add("bg-indigo-500/15");
            resultTitle.textContent = "Balance Énergétique Parfaite";
            resultDesc.textContent = "L'apport calorique de cette portion correspond exactement à la dépense basale estimée.";
        }

        // Animation d'apparition du résultat
        resultCard.classList.remove("hidden");
        setTimeout(() => {
            resultCard.classList.remove("scale-95", "opacity-0");
            resultCard.classList.add("scale-100", "opacity-100");
        }, 50);

    } catch (err) {
        showError(`Erreur lors de la prédiction : ${err.message}`);
        resultCard.classList.add("hidden");
    } finally {
        // Rétablir le bouton
        btnPredict.disabled = false;
        predictSpinner.classList.add("hidden");
        predictBtnText.textContent = "Prédire l'impact sur le poids";
    }
}
