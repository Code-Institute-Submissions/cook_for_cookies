// GLOBAL VARIABLES ------------------------------------------------------------

var ingredientDatabaseURL = "https://api.mlab.com/api/1/databases/onlinecookbook/collections/ingredients?apiKey=s7gyGaddJoxspRO2AkhmKaO0Wz0d_HH9";
var recipeDatabaseURL = 'https://api.mlab.com/api/1/databases/onlinecookbook/collections/recipes?apiKey=s7gyGaddJoxspRO2AkhmKaO0Wz0d_HH9';


// FUNCTIONS -------------------------------------------------------------------

function removeIngredientRows(){
    $('.inserted-ingredient-row').remove();
}

function loadData() {
    Promise.all([
        fetch(recipeDatabaseURL).then(response => response.json()).catch(),
        fetch(ingredientDatabaseURL).then(response => response.json()).catch(),
        removeIngredientRows()
    ]).then((response) => {
        prepareData(response)
    }).catch((error) => {
        console.log(error);
    });
}

function idToString(idData){
    var thisId1 = Object.values(idData._id);
    var thisIdExtracted = thisId1[0];
    return(thisIdExtracted)
}

function prepareData(data) {

    // This function adds the recipe ingredients to the ingredients table header

    const thisRecipeID = $('#recipe-id').val();
    const recipeData = data[0];
    const ingredientData = data[1];
    
    recipeData.forEach(function(recipe){
       var stringId = idToString(recipe);
       
       if(thisRecipeID === stringId){
           let thisRecipe = recipe;
           createThisRecipeIngredientsList(thisRecipe, ingredientData);
       }
    });
}    

function createThisRecipeIngredientsList(recipe, ingredients){
    if(recipe.recipe_ingredients === undefined){
        var newIngredientRow = "<tr class='inserted-ingredient-row'><td> There are currently no ingredients for this recipe. MES1</td><td>";
        $(newIngredientRow).insertAfter('.ingredients-table-header');
    } else {
        thisRecipeIngredients = [];
        
        for(i = 0; i < recipe.recipe_ingredients.length; i++){
            var ingredientId = Object.keys(recipe.recipe_ingredients[i]);
            var ingredientIdStr = ingredientId[0];
            ingredients.forEach(function(ingredient){
                var masterIngredientId = idToString(ingredient);
                if(masterIngredientId.replace(" ", "") === ingredientIdStr.replace(" ", "")){
                    ingredient.quantity = Object.values(recipe.recipe_ingredients[i]);
                    thisRecipeIngredients.push(ingredient);
                    }
                });
            }
        
        if (thisRecipeIngredients == []) {
            newIngredientRow = "<tr class='inserted-ingredient-row'><td> There are currently no ingredients for this recipe. MES1</td><td>";
            $(newIngredientRow).insertAfter('.ingredients-table-header');
        } else {
            thisRecipeIngredients.forEach(function(ingredient){
            var newIngredientRow = "<tr class='inserted-ingredient-row' id='" + idToString(ingredient) + "'><td>" + ingredient.ingredient_name + "</td><td>" + ingredient.quantity[0] + "</td><td><i class='remove fas fa-minus-square' type='button'></i></td></tr>";
            $(newIngredientRow).insertAfter('.ingredients-table-header');
            });    
        }        
    }
    
    removeIngredient();
}

function updateRecipe() {

    // This function will push updated information to the database without having to refresh the page...

    var recipeID = $('.recipe-id').val()

    $.ajax({
        url: '/update_recipe/' + recipeID,
        data: $('form').serialize(),
        type: 'POST',
        success: function(response) {
            console.log(response);
            loadData();
        },
        error: function(error) {
            console.log(error);
        }
    });
}

function dataToJSON(databaseExtract) {

    // This function converts any data pulled from MONGODB into a list of JSON objects

    var convertToString = JSON.stringify(databaseExtract);
    var revisedString = convertToString.replace(/u'/g, "'");
    var almostJsonData = JSON.parse(revisedString);
    var almostJsonData2 = almostJsonData.replace(/'/g, "\"");
    var jsonData = JSON.parse(almostJsonData2);

    return jsonData;
}

function removeIngredient(){
    $('.remove').on("click", function() {
        const rowId = $(this).closest("tr").attr("id");
        const thisRecipeID = $('#recipe-id').val();
        console.log(rowId + " " + thisRecipeID)
        
        $.ajax({
            url: '/delete_ingredient_from_recipe/' + thisRecipeID + '/' + rowId,
            type: 'POST',
            success: function(response) {
                console.log(response);
                loadData();
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
}

// DOCUMENT FUNCTIONS ----------------------------------------------------------

$(document).ready(function() {

    loadData();

    //  This is to close any pop up button...

    $('.hide-me-btn').on("click", function() {
        $('.hide-me').fadeOut("fast")
    });

    // This will make the button to confirm and actually delete a recipe appear

    $('.delete-recipe-btn').on("click", function() {
        $(this).next().show()
    });

    // This runs the update database function on click...

    $('.update-recipe-btn').click(function() {
        updateRecipe();
    });
});