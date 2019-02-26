var vm = new Vue({
  el: '#starting',
  delimiters: ['${', '}'],
  data: {
    ingredients: [],
    loading: false,
    currentIngredient: {},
    message: null,
    has_paginated:false,
    page:1,
    perPage: 10,
    pages:[],
    //COUPLED WITH BACKEND DO NOT REMOVE BELOW
    newIngredient: {
      'ingredient_name': '',
      'quantity': 0
    },
    sortKey: 'ingredient_name',
    sortAsc: [
      { 'ingredient_name': true },
      { 'package_size': true },
      { 'cpp': true },
      { 'description': true },
      { 'id': true }
    ],
    error:'',
  },
  mounted: function () {},
  methods: {
    getIngredients: function (skuid) {
      this.loading = true;
      this.$http.get('/api/ingredients_to_sku/' + skuid)
        .then((response) => {
          this.ingredients = response.data;
          this.loading = false;
          if(!this.has_paginated){
                      this.setPages();
                      this.has_paginated=true; 
                    }
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
          if((this.ingredients.length%this.perPage)==1){
                      this.deletePage();
                    }
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
          if((this.ingredients.length%this.perPage)==0){
            this.addPage();
         }
          this.getIngredients(skuid);
        })
        .catch((err) => {
          this.loading = false;
          this.error = err.bodyText;
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
        this.error = err.bodyText;
        console.log(err);
      })
    },
    setPages: function () {
        let numberOfPages = Math.ceil(this.ingredients.length / this.perPage);
        for (let index = 1; index <= numberOfPages; index++) {
          this.pages.push(index);
        }
      },
      addPage: function (){
          this.pages.push(Math.ceil(this.ingredients.length / this.perPage)+1);
      },
      deletePage: function (){
        this.pages=[];
          let numberOfPages = Math.ceil(this.ingredients.length / this.perPage);
        for (let index = 1; index < numberOfPages; index++) {
          this.pages.push(index);
        }
      },
      paginate: function (ingredients) {
      let page = this.page;
      // console.log(page)
      let perPage = this.perPage;
      let from = (page * perPage) - perPage;
      let to = (page * perPage);
      return  ingredients.slice(from, to);
    },
    sortBy: function (key) {
      this.sortKey = key
      this.sortAsc[key] = !this.sortAsc[key]
      if (!this.sortAsc[this.sortKey]) {
        this.ingredients = _.sortBy(this.ingredients, this.sortKey)
      } else {
        this.ingredients = _.sortBy(this.ingredients, this.sortKey).reverse()
      }
    },
  },
  computed: {
    displayedIngredients () {
      return this.paginate(this.ingredients);
    }
  },
});