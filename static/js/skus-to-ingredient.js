var vm = new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     skus: [],
     loading: false,
     //currentSku: {},
     message: null,
     //COUPLED WITH BACKEND DO NOT REMOVE BELOW
     //newSku: { 'ingredient_name': '', 'quantity':0 },
   },
   mounted: function() {},
   methods: {
       getIngredients: function(ingredientid){
           this.loading = true;
           this.$http.get('/api/skus_to_ingredient/'+ingredientid)
               .then((response) => {
                   this.skus = response.data;
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
   }
   });