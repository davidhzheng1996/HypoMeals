var vm = new Vue({
  el: '#starting',
  delimiters: ['${', '}'],
  data: {
    ingredients: [],
    loading: false,
    currentIngredient: {},
    message: null,
    //COUPLED WITH BACKEND DO NOT REMOVE BELOW
    newIngredient: {
      'ingredient_name': '',
      'quantity': 0
    },
  },
  mounted: function () {},
  methods: {
    getIngredients: function (skuid) {
      this.loading = true;
      this.$http.get('/api/ingredients_to_sku/' + skuid)
        .then((response) => {
          this.ingredients = response.data;
          this.loading = false;
        })
        .catch((err) => {
          this.loading = false;
          console.log(err);
        })
    },
    getIngredient: function (ingredientid) {
      for (key in this.ingredients) {
        // console.log('here')
        if (this.ingredients.hasOwnProperty(key)) {
          // console.log(this.goals[key].id)
          if (this.ingredients[key].id == ingredientid) {
            this.currentIngredient = {
              'ingredient_name': this.ingredients[key].ingredient_name,
              'quantity': this.ingredients[key].quantity,
              'id':this.ingredients[key].id
            }
            $("#editIngredientModal").modal('show');
          }
        }
      }
    },
    deleteIngredient: function (skuid, ingredientid) {
      this.loading = true;
      // TODO: use delimiters
      this.$http.post('../api/delete_ingredients_to_sku/' + skuid + '/' + ingredientid)
        .then((response) => {
          this.loading = false;
          this.getIngredients(skuid);
        })
        .catch((err) => {
          this.loading = false;
          console.log(err);
        })
    },
    addIngredient: function (skuid) {
      this.loading = true;
      this.newIngredient.ingredient_name = this.newIngredient.ingredient_name.toLowerCase();
      this.$http.post('/api/ingredients_to_sku/' + skuid, this.newIngredient)
        .then((response) => {
          $("#addIngredientModal").modal('hide');
          this.loading = false;
          this.getIngredients(skuid);
        })
        .catch((err) => {
          this.loading = false;
          console.log(err);
        })
    },
    updateIngredient: function (skuid,ingredientid) {
      this.loading = true;
      this.currentIngredient.ingredient_name = this.currentIngredient.ingredient_name.toLowerCase();
        this.$http.post('../api/update_ingredients_to_sku/' + skuid+ '/'+ingredientid,this.currentIngredient)
          .then((response) => {
            $("#editIngredientModal").modal('hide');
            this.loading = false;
            this.getIngredients(skuid);
        })
          .catch((err) => {
        this.loading = false;
        console.log(err);
      })
    }
  }
});