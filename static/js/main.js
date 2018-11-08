// GLOBAL VARIABLES ------------------------------------------------------------

var ingredientDatabaseURL = "https://api.mlab.com/api/1/databases/onlinecookbook/collections/ingredients?apiKey=s7gyGaddJoxspRO2AkhmKaO0Wz0d_HH9";
var recipeDatabaseURL = 'https://api.mlab.com/api/1/databases/onlinecookbook/collections/recipes?apiKey=s7gyGaddJoxspRO2AkhmKaO0Wz0d_HH9';

var defaultIngredientImage = "https://images.unsplash.com/photo-1538140177897-d71d1643349e?ixlib=rb-0.3.5&ixid=eyJhcHBfaWQiOjEyMDd9&s=058d4a817fafacf72008b4fe55a4f07f&auto=format&fit=crop&w=500&q=60"

// FUNCTIONS -------------------------------------------------------------------
function sortIngredients(a, b) {
    // Use toUpperCase() to ignore character casing
    const ingredientNameA = a.ingredient_name.toUpperCase();
    const ingredientNameB = b.ingredient_name.toUpperCase();

    let comparison = 0;
    if (ingredientNameA > ingredientNameB) {
        comparison = - 1;
    }
    else if (ingredientNameA < ingredientNameB) {
        comparison = 1;
    }
    return comparison;
}


function removeExistingRows() {
    $('.inserted-ingredient-row').remove();
    $('.inserted-instruction-row').remove();
}

function showDataRows(){
    $('.instructions-list-table').fadeIn(500);
    $('.ingredients-list-table').fadeIn(500);
}

function loadData() {
    Promise.all([
        fetch(recipeDatabaseURL).then(response => response.json()).catch(),
        fetch(ingredientDatabaseURL).then(response => response.json()).catch(),
        removeExistingRows()
    ]).then((response) => {
        prepareData(response);
        showDataRows();
    }).catch((error) => {
        console.log(error);
        flashedMessage("Oops, an error has occured.  Please try later")
    });
}

function idToString(idData) {
    var thisId1 = Object.values(idData._id);
    var thisIdExtracted = thisId1[0];
    return (thisIdExtracted);
}

function prepareData(data) {

    // This function adds the recipe ingredients to the ingredients table header

    const thisRecipeID = $('#recipe-id').val();
    const recipeData = data[0];
    const ingredientData = data[1];
    
    recipeData.forEach(function(recipe) {
        var stringId = idToString(recipe);
        if (thisRecipeID === stringId) {
            let thisRecipe = recipe;
            createThisRecipeData(thisRecipe, ingredientData);
        }
    });
}

function createThisRecipeData(recipe, ingredients) {
    if (recipe.recipe_instructions === undefined || recipe.recipe_instructions.length === 0){
        if ($('.no-instructions-row').length === 0){
            $('.instructions-table-header').hide();
            newInstructionRow = "<tr class='no-instructions-row spill-text'><td> There are currently no instructions for this recipe.</td>";
            $('.instructions-list-table').after(newInstructionRow);    
        }
    } else {
        $('.instructions-table-header').show();
        sortedInstructions = recipe.recipe_instructions.sort(function(a, b){
            return b.step - a.step;
        });
        
        if($('.edit-recipe-section').length === 1){
            sortedInstructions.forEach(function(instruction) {
                
                var newInstructionRow = "<tr class='inserted-instruction-row' id='" 
                + instruction.step 
                + "'><td class='step-no'>" 
                + instruction.step 
                + "</td><td>" 
                + instruction.instruction 
                + "</td><td><i class='remove remove-instruction fas fa-minus-square' type='button'></i></td></tr>";
                
                $('.instructions-list-table').after(newInstructionRow);
            });    
        } else {
            sortedInstructions.forEach(function(instruction) {
                var newInstructionRow = "<tr class='inserted-instruction-row' id='" + instruction.step + "><td>" + instruction.step + "</td><td>" + instruction.instruction + "</td></tr>";
                $('.instructions-list-table').after(newInstructionRow);
            });
         }
    }
    
    $('.new-instructions-box').val("");
    
    if (recipe.recipe_ingredients !== undefined && recipe.recipe_ingredients.length !== 0) {
        thisRecipeIngredients = [];

        for (i = 0; i < recipe.recipe_ingredients.length; i++) {
            var ingredientId = Object.keys(recipe.recipe_ingredients[i]);
            var ingredientIdStr = ingredientId[0];
            ingredients.forEach(function(ingredient) {
                var masterIngredientId = idToString(ingredient);
                if (masterIngredientId.replace(" ", "") === ingredientIdStr.replace(" ", "")) {
                    ingredient.quantity = Object.values(recipe.recipe_ingredients[i]);
                    thisRecipeIngredients.push(ingredient);
                }
            });
        }
    
        if (thisRecipeIngredients != []) {
            const sortedIngredients = thisRecipeIngredients.sort(sortIngredients);
            
            if($('.edit-recipe-section').length === 1){
                sortedIngredients.forEach(function(ingredient) {
                    if (ingredient.ingredient_image_url === undefined || ingredient.ingredient_image_url === ""){
                        var imageSrc = defaultIngredientImage;
                    } else {
                        var imageSrc = ingredient.ingredient_image_url;
                    }
                    
                    var newIngredientRow = "<tr class='inserted-ingredient-row' id='" 
                        + idToString(ingredient) 
                        + "'><td><img src='" 
                        + imageSrc + "'</td><td>" 
                        + ingredient.ingredient_name 
                        + "</td><td>" 
                        + ingredient.quantity[0] 
                        + "</td><td><i class='remove remove-ingredient fas fa-minus-square' type='button'></i></td></tr>";
                        
                    $('.ingredients-table-header').after(newIngredientRow);
                });    
            } else {
                sortedIngredients.forEach(function(ingredient) {
                    if (ingredient.ingredient_image_url === undefined || ingredient.ingredient_image_url === ""){
                        var imageSrc = defaultIngredientImage;
                    } else {
                        var imageSrc = ingredient.ingredient_image_url;
                    }
                    
                    var newIngredientRow = "<tr class='inserted-ingredient-row' id='" 
                    + idToString(ingredient) 
                    + "'><td><img src='" 
                    + imageSrc + "'</td><td>" 
                    + ingredient.ingredient_name 
                    + "</td><td>" 
                    + ingredient.quantity[0] 
                    + "</td></tr>";
                    
                    $('.ingredients-table-header').after(newIngredientRow);
                });
            }
        } 
    } else {
        // This adds a line to the page if there are no ingredients to display
        if ($('.no-ingredients-row').length === 0){
            $('.ingredients-table-header').hide();
            newIngredientRow = "<tr class='no-ingredients-row spill-text'><td> There are currently no ingredients for this recipe.</td>";
            $('.ingredients-list-table').after(newIngredientRow);
        }
    }

    $('.ingredient-box').val("");
    // This will enable the user to remove ingredients without having to reload the page and acts as both a listener and a function to action call
    removeIngredient();
    removeInstruction();
}

function updateRecipe(section) {

    // This function will push updated information to the database without having to refresh the page...

    var recipeID = $('.recipe-id').val()

    $.ajax({
        url: '/update_recipe/' + section + '/' + recipeID,
        data: $('form').serialize(),
        type: 'POST',
        success: function(response) {
            console.log(response);
            loadData();
            if(section == 1){
                flashedMessage("Updated!")
            }
        },
        error: function(error) {
            console.log(error);
            flashedMessage("Oops, an error has occured.  Please try later");
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

function removeIngredient() {
    $('.remove-ingredient').on("click", function() {
        const rowId = $(this).closest("tr").attr("id");
        const thisRecipeID = $('#recipe-id').val();

        $.ajax({
            url: '/delete_ingredient_from_recipe/' + thisRecipeID + '/' + rowId,
            type: 'POST',
            success: function(response) {
                console.log(response);
                loadData();
            },
            error: function(error) {
                console.log(error);
                flashedMessage("Oops, an error has occured.  Please try later");
            }
        });
    });
}

function removeInstruction() {
    $('.remove-instruction').on("click", function() {
        const rowId = $(this).closest("tr").attr("id");
        const thisRecipeID = $('#recipe-id').val();

        $.ajax({
            url: '/delete_instruction_from_recipe/' + thisRecipeID + '/' + rowId,
            type: 'POST',
            success: function(response) {
                console.log(response);
                loadData();
            },
            error: function(error) {
                console.log(error);
                flashedMessage("Oops, an error has occured.  Please try later")
            }
        });
    });
}

function flashedMessage(message) {
    $('.flashed-message').text(message);
    $('.round-pop-up-container').show();
}

function fadeInHomeTitle(delay){
    setTimeout(function(){
        $('.welcome-message').removeClass("no-opacity");
        $('.welcome-message').addClass("fade-in-text");
    }, delay);
    setTimeout(function(){
        $('.welcome-para-container').removeClass("no-opacity");
        $('.welcome-para-container').addClass("fade-in-text");
    }, delay + 2000);
}

function showBoxOnHover(hoverItem, displayBox){
    $(hoverItem).mouseover(function() {
        $(displayBox).fadeIn("fast");
  })
  .mouseout(function() {
    $(displayBox).fadeOut("fast");
  });
}

function zoomImage(hoverElement, pictureElement){
    $(hoverElement).mouseover(function() {
        $(pictureElement).addClass("grow-pic");
}).mouseout(function() {
    $(pictureElement).removeClass("grow-pic");
  });
}

// DOCUMENT FUNCTIONS ----------------------------------------------------------

$(document).ready(function() {
    
    loadData();

    //  This is to close any pop up button...

    $('.hide-me-btn').on("click", function() {
        $('.hide-me').fadeOut("fast")
    });

    // This will make the button to confirm and actually delete a recipe appear or disappear on cancel

    $('.delete-recipe-btn').on("click", function() {
        $(this).parent().siblings().slideDown();
        
    });
    
    $('.cancel-delete-recipe-btn').on("click", function() {
        $(this).parent().closest('.delete-recipe-row').slideUp();
        
    });
    
    // This runs the update database function on click...

    $('.update-section1-btn').click(function() {
        updateRecipe(1);
    });

    $('.add-instructions-btn').click(function() {
        if($('#step').val() == ""){
            flashedMessage("Don't forget to enter a step no!");
            $('html, body').animate({
                scrollTop: ($('.edit-recipe-section').offset().top)
            },500);
        } else {
            $('.no-instructions-row').remove();
            updateRecipe(2);
        }
    });
    
    $('.add-ingredients-btn').click(function() {
        if($('#ingredient_quantity').val() == ""){
            flashedMessage("Don't forget to enter a quantity!");
            $('html, body').animate({
                scrollTop: ($('.edit-recipe-section').offset().top)
            },500);
        } else {
            $('.no-ingredients-row').remove();
            $('.ingredients-table-header').show();
            updateRecipe(3);
        }
    });
    
    fadeInHomeTitle(1000);
    
    setTimeout(function(){
        $('.pre-slide-in-from-left').addClass('slide-in-from-left');
        $('.pre-slide-in-from-right').addClass('slide-in-from-right');
    }, 1000);
    
    showBoxOnHover(".user-photo-instructions-btn", '.user-photo-instructions');
    
    zoomImage('.fa-file-alt', '.leaderboard-intro-bg');
    zoomImage('.sign-up-btn', '.sign-up-bg');
    zoomImage('.log-in-btn', '.log-in-bg');
    
});
