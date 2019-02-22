var vm = new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     formulas: [],
     loading: false,
     //currentSku: {},
     message: null,
     //COUPLED WITH BACKEND DO NOT REMOVE BELOW
     //newSku: { 'ingredient_name': '', 'quantity':0 },
   },
   mounted: function() {},
   methods: {
       getFormula: function(formulaid){
           this.loading = true;
           this.$http.get('/api/formula_to_sku/'+formulaid)
               .then((response) => {
                   this.formulas = response.data;
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       viewIngredients: function(formulaid){
        window.location.href = '/formula/'+formulaid
      },

   },
   });