// https://codesandbox.io/s/o29j95wx9
new Vue({
     el: '#starting',
     delimiters: ['${','}'],
  data: {
     ingredients: [],
     loading: false,
     currentIngredient: {},
     message: null,
     page:1,
     perPage: 3,
     pages:[],
     newIngredient: { 'ingredient_name': '', 'id': null, 'description': null,'package_size': '', 'cpp': 0, 'comment': null,},
     ingredientFile: null,
     search_term: '',
     search_suggestions: search_suggestions,
     search_input: '',
     has_paginated:false,
     csv_uploaded:false,
     // what is this for???
     suggestionAttribute: 'original_title',

     // sorting variables
     sortKey: 'ingredient_name',
     sortAsc: [
            { 'ingredient_name': true },
            { 'package_size': true },
            { 'cpp': true },
            { 'description': true },
            {'id': true}
          ],
     // File Upload Errors
     upload_errors: '',
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
                   this.lowerCaseName();
                   if(!this.has_paginated){
                      this.setPages();
                      this.has_paginated=true; 
                    }
                    if(this.csv_uploaded){
                      this.pages=[];
                      this.setPages();
                      this.csv_uploaded=false;
                    }
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
                   if((this.ingredients.length%this.perPage)==1){
                      this.deletePage();
                    }
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
         for(let index = 0; index<this.ingredients.length; index++){
            if(this.newIngredient.ingredient_name.toLowerCase().trim()===(this.ingredients[index].ingredient_name.toLowerCase().trim())){
                this.message = "already exists";
                return;
                //console.log(err);
            }
          }
         if((this.ingredients.length%this.perPage)==0){
            this.addPage();
         }
         this.getIngredients();
         //ingredients.append(this.newingredient)
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
       },
       lowerCaseName: function(){
          for(let index = 0; index<this.ingredients.length; index++){
            this.ingredients[index].ingredient_name = this.ingredients[index].ingredient_name.toLowerCase().trim();
          }
       },
       updateIngredient: function() {
         this.loading = true;
         // console.log(this.currentIngredient)
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
      setPages: function () {
        //this.pages = []
        let numberOfPages = Math.ceil(this.ingredients.length / this.perPage);
        for (let index = 1; index <= numberOfPages; index++) {
          this.pages.push(index);
        }
                    //         for(let i = 0; i < pages.length;i++){
                    //   console.log(pages[i]);
                    // }
        //console.log(pages);
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
             console.log(response.data)
            this.upload_errors = response.data['errors'].join('\n') + response.data['warnings'].join('\n')
         this.loading = false;
         this.csv_uploaded=true;
         this.getIngredients();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
        })
      },

      exportIngredientCSV: function() {
        this.loading = true;
        // Export all current ingredients to a csv file
        // https://codepen.io/dimaZubkov/pen/eKGdxN
        let csvContent = "data:text/csv;charset=utf-8,";
        csvContent += [
          Object.keys(this.ingredients[0]).join(","),
          // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax
          ...this.ingredients.map(key => Object.values(key).join(","))
        ].join("\n");
        const url = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "ingredient.csv");
        link.click();
        // Export the entire ingredient database as CSV 
        // this.$http.get('/api/ingredient_export/')
        //   .then((response) => {
        //         // https://thewebtier.com/snippets/download-files-with-axios/
        //         // https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL
        //         // url to the csv file in form of a Blob
        //         // url lifetime is tied to the document in the window
        //         const url = window.URL.createObjectURL(new Blob([response.data]));
        //         // create a link with the file url and click on it
        //         const link = document.createElement('a');
        //         link.href = url;
        //         link.setAttribute('download', 'ingredient.csv');
        //         document.body.appendChild(link);
        //         link.click();
                
        //         this.loading = false;
        //         this.getIngredients();
        //   }).catch((err) => {
        //         this.loading = false;
        //         console.log(err)
        //   })
      },

      selectIngredient: function(){
            //let api_url = '/api/ingredient/';
           // https://medium.com/quick-code/searchfilter-using-django-and-vue-js-215af82e12cd
           // if(this.search_term !== '' || this.search_term !== null) {
           //      api_url = '/api/ingredient/?search=' + this.search_term
           // }
           let api_url = '/api/ingredient/';
           this.loading = true;
           this.$http.get(api_url)
               .then((response) => {
                   this.ingredients = response.data;
                   this.loading = false;
                   $("#selectIngredientModal").modal('show');
                   this.lowerCaseName();
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
      },
            // Input assistance 
      search_input_changed: function() {
        const that = this
        this.$http.get('/api/ingredient/?search=' + this.search_term)
                .then((response) => {
                        for (var i in response.data) {
                                this.search_suggestions.push(response.data[i].ingredient_name)
                        }
                })
      },

      // https://vuejs.org/v2/guide/migration.html#Replacing-the-orderBy-Filter
      sortBy: function(key) {
        this.sortKey = key
        this.sortAsc[key] = !this.sortAsc[key]
        if(!this.sortAsc[this.sortKey]){
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

  // watch: {
  //   ingredients () {
  //     this.setPages();
  //   }
  // }, 
   });
