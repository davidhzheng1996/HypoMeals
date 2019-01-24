new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     ingredients: [],
     loading: false,
     currentIngredient: {},
     message: null,
     newIngredient: { 'name': 'Potato', 'id': null, 'description': null,'package_size': '3', 'cpp': 20, },
   },
   mounted: function() {
       this.getIngredients();
   },
   methods: {
       getIngredients: function(){
           this.loading = true;
           this.$http.get('/api/ingredient/')
               .then((response) => {
                   this.ingredients = response.data;
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       getIngredient: function(id){
           this.loading = true;
           this.$http.get('/api/ingredient/'+id+'/')
               .then((response) => {
                   this.currentIngredient = response.data;
                   $("#editIngredientModal").modal('show');
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       deleteIngredient: function(id){
         this.loading = true;
         // TODO: use delimiters
         this.$http.delete('/api/ingredient/' + id + '/')
           .then((response) => {
             this.loading = false;
             this.getIngredients();
           })
           .catch((err) => {
             this.loading = false;
             console.log(err);
           })
       },
       addIngredient: function() {
         this.loading = true;
         this.$http.post('/api/ingredient/',this.newIngredient)
           .then((response) => {
         $("#addIngredientModal").modal('hide');
         this.loading = false;
         this.getIngredients();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
       },
       updateIngredient: function() {
         this.loading = true;
         console.log(this.currentIngredient)
         this.$http.put('/api/ingredient/'+ this.currentIngredient.id + '/',     this.currentIngredient)
           .then((response) => {
             $("#editIngredientModal").modal('hide');
         this.loading = false;
         this.currentIngredient = response.data;
         this.getIngredients();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
   }
   
   
   }
   });