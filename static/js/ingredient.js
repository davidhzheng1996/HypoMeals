new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     ingredients: [],
     loading: false,
     currentIngredient: {},
     message: null,
     newIngredient: { 'ingredient_name': '', 'id': null, 'description': null,'package_size': '', 'cpp': 0, 'comment': null,},
     ingredientFile: null,
     search_term: ''
   },
   mounted: function() {
       this.getIngredients();
   },
   methods: {
       getIngredients: function(){
           let api_url = '/api/ingredient/';
           // https://medium.com/quick-code/searchfilter-using-django-and-vue-js-215af82e12cd
           if(this.search_term !== '' || this.search_term !== null) {
                api_url = '/api/ingredient/?search=' + this.search_term
           }
           this.loading = true;
           this.$http.get(api_url)
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
        this.ingredientFile = event.target.files[0]
      },
        
      uploadIngredientCSV: function() {
        this.loading = true;
        // upload this.ingredientCSV to REST api in FormData
        const formData = new FormData()
        // https://developer.mozilla.org/en-US/docs/Web/API/FormData/append
        formData.append('file', this.ingredientFile, this.ingredientFile.name)
        this.$http.post('/api/ingredient_import/', formData)
           .then((response) => {
         this.loading = false;
         this.getIngredients();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
        })
      },

      exportIngredientCSV: function() {
        this.loading = true;
        this.$http.get('/api/ingredient_export/')
          .then((response) => {
                // https://thewebtier.com/snippets/download-files-with-axios/
                // https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL
                // url to the csv file in form of a Blob
                // url lifetime is tied to the document in the window
                const url = window.URL.createObjectURL(new Blob([response.data]));
                // create a link with the file url and click on it
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', 'ingredient.csv');
                document.body.appendChild(link);
                link.click();
                
                this.loading = false;
                this.getIngredients();
          }).catch((err) => {
                this.loading = false;
                console.log(err)
          })
      },

   }
   });