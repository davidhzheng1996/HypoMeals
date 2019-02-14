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
     perPage: 10,
     pages:[],
     newIngredient: { 'ingredient_name': '', 'id': null, 'description': null,'package_size': '', 'cpp': 0, 'comment': null,},
     ingredientFile: null,
     search_term: '',
     search_input: '',
     has_paginated:false,
     csv_uploaded:false,
     has_searched: false,
     search_suggestions: [],
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
           if(this.search_term !== '' && this.search_term !== null) {
                api_url = '/api/ingredient/?search=' + this.search_term
           }
           //console.log(this.search_term);
           this.loading = true;
           this.$http.get(api_url)
               .then((response) => {
                   this.ingredients = response.data;
                   this.loading = false;
                   if(!this.has_paginated){
                      this.setPages();
                      this.has_paginated=true; 
                    }
                    if(this.csv_uploaded){
                      this.pages=[];
                      this.setPages();
                      this.csv_uploaded=false;
                    }

                    if(!this.has_searched) {
                    let allTerms = []
                    for(key in this.ingredients){
                      if(this.ingredients.hasOwnProperty(key)){
                        allTerms.push(this.ingredients[key].ingredient_name)
                       this.has_searched = true;
                      }
                    }
                      $( "#search_input_id" ).autocomplete({
                      minLength:1,   
                      delay:500,   
                      source: allTerms,
                      select: function(event,ui){
                        this.search_term = ui.item.value
                      }
                        });
                   }
     

               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       viewIngredient: function(ingredientid){
        window.location.href = '/ingredient/'+ingredientid
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
         this.has_searched = false;
         for(let index = 0; index<this.ingredients.length; index++){
            if(this.newIngredient.ingredient_name.toLowerCase()===this.ingredients[index].ingredient_name.toLowerCase()){
                console.log("Already exists");
                return;
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
       updateIngredient: function() {
         this.loading = true;
         this.$http.put('/api/ingredient/'+ this.currentIngredient.id + '/',     this.currentIngredient)
           .then((response) => {
             $("#editIngredientModal").modal('hide');
         this.loading = false;
         this.currentIngredient = response.data;
         for(let index = 0; index<this.ingredients.length; index++){
            if(this.newIngredient.ingredient_name.toLowerCase()===this.ingredients[index].ingredient_name.toLowerCase()){
                console.log("Already exists");
                return;
            }
          }
         this.getIngredients();
         })
           .catch((err) => {
         this.loading = false;
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
            this.upload_errors = response.data['errors'].join('\n') + response.data['warnings'].join('\n')
         this.loading = false;
         this.csv_uploaded=true;
         this.getIngredients();
         })
           .catch((err) => {
            this.upload_errors = err.data['errors'].join('\n') + err.data['warnings'].join('\n')
         this.loading = false;
         console.log(err);
        })
      },

      exportIngredientCSV: function() {
        this.loading = true;
        // Export all current ingredients to a csv file
        // https://codepen.io/dimaZubkov/pen/eKGdxN
        let csvContent = "data:text/csv;charset=utf-8,";
        //console.log(this.ingredients[0])
        csvContent += [
          Object.keys(this.ingredients[0]).join(","),
          // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax
          ...this.ingredients.map(key => Object.values(key).join(","))
        ].join("\n");
        // console.log(csvContent)
        const url = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "ingredient.csv");
        link.click();
      },


        createReport: function(){
        this.loading = true;
        // Export all current ingredients to a csv file
        // https://codepen.io/dimaZubkov/pen/eKGdxN
        let csvContent = "data:text/csv;charset=utf-8,";
        csvContent+=[["ingredient", "sku"].join(",")+'\n'];
        let c = 0
        //console.log(csvContent);
        for (let i = 0; i < this.ingredients.length; i++) {
                //console.log(this.ingredients[key].ingredient_name)
                this.$http.get('/api/skus_to_ingredient/'+this.ingredients[i].id)
               .then((response) => {
                  c = c + 1;
                   var skus = [];
                   this.skus = response.data;
                   for(let j = 0; j < this.skus.length; j++){
                        // console.log(this.ingredients[i].ingredient_name)
                        // console.log(this.skus[j].sku_name)
                        csvContent+=[[this.ingredients[i].ingredient_name,this.skus[j].sku_name].join(",")+'\n'];
                        //console.log(csvContent);
                      
                   }
                  // this.finished();
                  if(c==this.ingredients.length){
                     console.log(csvContent);
                   
                     const url = encodeURI(csvContent);
                    const link = document.createElement("a");
                     link.setAttribute("href", url);
                     link.setAttribute("download", "dependency.csv");
                     link.click();
                 }
                   this.loading = false;
                   //this.has_called = true; 
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
         // console.log(csvContent);

        } 
      

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
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
      },

      search_input_changed: function() {
        this.getIngredients();
      },

      // Trigger an action to update search_term
      // Dirty trick to get around a VueJS bug: https://github.com/vuejs/vue/issues/5248 
      onBlur: function(event) {
        if (event && this.search_term !== event.target.value) 
          this.search_term = event.target.value
      },

      getSkus: function(ingredientid){
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
  
  
   });