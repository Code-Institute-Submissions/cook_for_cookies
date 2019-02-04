describe("Game Functions", function() {

    beforeEach(function() {
        testRecipeCommentsDB = [
            {"_id": {"$oid": "5c41fa61c8efe56c292423f0"},
            "reviewing_user": "caianroma@yahoo.co.uk", "review_comments": "New Review",
            "reviewed_recipe_id": "5be462231a7c58000cd2d860","review_score": "4"},
            {"_id": {"$oid": "5c41fb42c8efe56c292423f1"}, "reviewing_user": "c@yahoo.com",
            "review_comments": "Very yummy", "reviewed_recipe_id": "5be462231a7c58000cd2d860",
            "review_score": "2"},
            {"_id": {"$oid": "5c45e4cfa23da6000c091cc8"}, "reviewed_recipe_id": "5be462231a7c58000cd2d860",
            "reviewing_user": "lil.fiorletta@yahoo.co.uk", "review_comments": "I love chocolate cake, please make me one.",
            "review_score": "3"}
            ];
    });

    describe("Initialise", function() {
        it("should return a pass to ensure that Jasmine has initialised properly (1 + 1 = 2)", function() {
            expect(onePlusOne()).toBe(2);
        });
    });
    
    describe("Data extraction", function() {
        it("should return the average score for any given recipe", function() {
            expect(calcRecipeScore(testRecipeCommentsDB)).toBe(3);
        });
    });
})