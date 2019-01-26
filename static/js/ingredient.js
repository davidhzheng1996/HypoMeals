new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     ingredients: [],
     loading: false,
     currentIngredient: {},
     message: null,
     newIngredient: { 'ingredient_name': '', 'id': null, 'description': null,'package_size': '', 'cpp': 0, 'comment': null,},
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
      },
      // https://www.academind.com/learn/vue-js/snippets/image-upload/
      selectIngredientCSV: function(event) {
        this.ingredientCSV = event.target.files[0]
        console.log(this.ingredientCSV)
        console.log('select csv');
      },
        
      uploadIngredientCSV: function() {
        console.log('upload csv');
        // upload this.ingredientCSV to REST api in FormData or Binary data
        const formData = new FormData()
        formData.append('ingredient_csv', this.selectedFile, this.selectedFile.name)
        axios.post('my-domain.com/file-upload', formData)
      },

   
   
   }
   });