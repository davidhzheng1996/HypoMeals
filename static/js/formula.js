Vue.filter('lowercase', function (value) {
   return value.toLowerCase()
})
new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     formulas: [],
     loading: false,
     query:'',
     currentFormula: {},
     message: null,
     page:1,
     perPage: 10,
     pages:[],
     newFormula: { 'formula_name': '', 'id': null, 'comment': null},
     formulaFile: null,
     has_paginated:false,
     csv_uploaded:false,
     search_term: '',
     search_suggestions: search_suggestions,
     search_input: '',
     has_searched: false,

     suggestionAttribute: 'original_title',

     sortKey: 'forumla_name',
     sortAsc: [
            { 'formula_name': true },
            { 'id': true },
          ],
      upload_errors: '',
   },
   mounted: function() {
       this.getFormulas();
   },
   methods: {
       getFormulas: function(){
          let api_url = '/api/formula/';
           // https://medium.com/quick-code/searchfilter-using-django-and-vue-js-215af82e12cd
           if(this.search_term !== '' && this.search_term !== null) {
                api_url = '/api/formula/?search=' + this.search_term;
           }
           this.loading = true;
           this.$http.get(api_url)
               .then((response) => {
                   this.formulas = response.data;
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
                      for(key in this.formulas){
                        if(this.formulas.hasOwnProperty(key)){
                          allTerms.push(this.formulas[key].formula_name)
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
       getFormula: function(id){
           this.loading = true;
           this.$http.get('/api/formula/'+id+'/')
               .then((response) => {
                   this.currentFormula = response.data;
                   $("#editFormulaModal").modal('show');
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
       },
       deleteFormula: function(id){
         this.loading = true;
         // TODO: use delimiters
         this.$http.delete('/api/formula/' + id + '/')
           .then((response) => {
             this.loading = false;
                    if((this.formulas.length%this.perPage)==1){
                      this.deletePage();
                    }
             this.getFormulas();
           })
           .catch((err) => {
             this.loading = false;
             console.log(err);
           })
       },
      setPages: function () {
        let numberOfPages = Math.ceil(this.formulas.length / this.perPage);
        for (let index = 1; index <= numberOfPages; index++) {
          this.pages.push(index);
        }
      },
      viewFormula: function(formulaid){
        window.location.href = '/formula/'+formulaid
      },
      viewSku: function(formulaid){
        window.location.href = '/show_formula/'+formulaid
      },
      addPage: function (){
          this.pages.push(Math.ceil(this.formulas.length / this.perPage)+1);
      },
      deletePage: function (){
        this.formulas=[];
          let numberOfPages = Math.ceil(this.formulas.length / this.perPage);
        for (let index = 1; index < numberOfPages; index++) {
          this.pages.push(index);
        }
      },
      paginate: function (formulas) {
      let page = this.page;
      let perPage = this.perPage;
      let from = (page * perPage) - perPage;
      let to = (page * perPage);
      return  formulas.slice(from, to);
    },
       addFormula: function() {
         this.loading = true;
         this.$http.post('/api/formula/',this.newFormula)
           .then((response) => {
         $("#addFormulaModal").modal('hide');
         this.loading = false;
         this.has_searched = false;
         // for(let index = 0; index<this.skus.length; index++){
         //    if(this.newSku.sku_name.toLowerCase()===this.skus[index].sku_name.toLowerCase()){
         //        console.log("Already exists");
         //        return;
         //    }
         //  }
         if((this.formulas.length%this.perPage)==0){
            this.addPage();
         }
         this.getFormulas();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
       },
       updateFormula: function() {
         this.loading = true;
         this.$http.put('/api/formula/'+ this.currentFormula.id + '/',     this.currentFormula)
           .then((response) => {
             $("#editFormulaModal").modal('hide');
         this.loading = false;
         this.currentFormula = response.data;
         this.getFormulas();
         })
           .catch((err) => {
         this.loading = false;
         console.log(err);
       })
   },

      selectFormulaCSV: function(event) {
        this.formulaFile = event.target.files[0]
      },
        
      uploadFormulaCSV: function() {
        if (this.formulaFile === null) {
          return;
        }
        this.loading = true;
        // upload this.ingredientCSV to REST api in FormData
        const formData = new FormData()
        // https://developer.mozilla.org/en-US/docs/Web/API/FormData/append
        formData.append('file', this.formulaFile, this.formulaFile.name)
        this.$http.post('/api/formula_import/', formData)
           .then((response) => {
            this.upload_errors = response.data['errors'].join('\n') + response.data['warnings'].join('\n')
            console.log(this.upload_errors)
         this.loading = false;
         this.csv_uploaded=true;
         this.getFormulas();
         })
           .catch((err) => {
            this.upload_errors = err.data['errors'].join('\n') + err.data['warnings'].join('\n')
         this.loading = false;
         console.log(err);
        })
      },

      // exportFormula: function(){
      //   this.loading = true;
      //   // Export all current ingredients to a csv file
      //   // https://codepen.io/dimaZubkov/pen/eKGdxN
      //   let csvContent = "data:text/csv;charset=utf-8,";

      //   csvContent+=[["Formula ID", "Ingr ID", "Quantity"].join(",")+'\n'];
      //   let c = 0
      //   //console.log(csvContent);
      //   for (let i = 0; i < this.formulas.length; i++) {
      //           //console.log(this.ingredients[key].ingredient_name)
      //           this.$http.get('/api/ingredients_to_formula/'+this.formulas[i].id)
      //          .then((response) => {
      //             c = c + 1;
      //              var ingredients = [];
      //              this.ingredients = response.data;
      //              for(let j = 0; j < this.ingredients.length; j++){
      //                   csvContent+=[[this.formulas[i].id,this.ingredients[j].id, this.ingredients[j].quantity].join(",")+'\n'];
                      
      //              }
      //             // this.finished();
      //             if(c==this.formulas.length){
      //                console.log(csvContent);
                   
      //                const url = encodeURI(csvContent);
      //                 const link = document.createElement("a");
      //                link.setAttribute("href", url);
      //                link.setAttribute("download", "formulas.csv");
      //                link.click();
      //            }
      //              this.loading = false;
      //              //this.has_called = true; 
      //          })
      //          .catch((err) => {
      //              this.loading = false;
      //              console.log(err);
      //          })

      //   } 
      

      // },

        sortBy: function(key) {
        this.sortKey = key
        this.sortAsc[key] = !this.sortAsc[key]
        if(!this.sortAsc[this.sortKey]){
          this.formulas = _.sortBy(this.formulas, this.sortKey)
        } else {
          this.formulas = _.sortBy(this.formulas, this.sortKey).reverse()
        }
      },
      
      onBlur: function(event) {
        if (event && this.search_term !== event.target.value) 
          this.search_term = event.target.value
      },
   
   },


  computed: {
    displayedFormulas () {
      return this.paginate(this.formulas);
    }
  },

   });