from recipe.models import Recipe,RecipeDetail,RecipeIngredient

# r = Recipe(recipe_name="c2")
# r.save()
# ri1 = RecipeIngredient(name = "chenpi")
# ri2 = RecipeIngredient(name = "water")
# ri3 = RecipeIngredient(name = "sugar")
# ri1.save()
# ri2.save()
# ri3.save()
# rd1 = RecipeDetail(recipe = r, ingredient = ri1,quantity = 100,unit = 'g')
# rd2 = RecipeDetail(recipe = r, ingredient = ri2,quantity = 300,unit = 'g')
# rd3 = RecipeDetail(recipe = r, ingredient = ri3,quantity = 150,unit = 'g')
# rd1.save()
# rd2.save()
# rd3.save()


r = Recipe.objects.get(recipe_name="c1")
r.save()
ri3 = RecipeIngredient(name = "jiang")
# ri1.save()
# ri2.save()
ri3.save()
ri1 = RecipeIngredient.objects.get(name = 'chenpi')
ri2 = RecipeIngredient.objects.get(name = 'water')
rd1 = RecipeDetail(recipe = r, ingredient = ri1,quantity = 160,unit = 'g')
rd2 = RecipeDetail(recipe = r, ingredient = ri2,quantity = 330,unit = 'g')
rd3 = RecipeDetail(recipe = r, ingredient = ri3,quantity = 160,unit = 'g')
rd1.save()
rd2.save()
rd3.save()


