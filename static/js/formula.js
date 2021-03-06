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
     newFormula: { 'formula_name': '', 'id': 0, 'comment': null},
     formulaFile: null,
     has_paginated:false,
     csv_uploaded:false,
     disable_paginate: false,
     search_term: '',
     search_input: '',
     suggestionAttribute: 'original_title',

     sortKey: 'forumla_name',
     sortAsc: [
            { 'formula_name': true },
            { 'id': true },
          ],
      upload_errors: '',
      name_error: '',
      error:'',
      test:'',
   },
   mounted: function() {
       this.getFormulas();
       $("#search_input_id").autocomplete({
        minLength: 2,
        delay: 100,
        source: function (request, response) {
          $.ajax({
            url: "/api/formula",
            dataType: "json",
            data: {
              search: request.term
            },
            success: function (data) {
              formula_names = $.map(data, function (item) {
                return [item.formula_name];
              })
              response(formula_names);
            }
          });
        },
        messages: {
          noResults: '',
          results: function() {}
        }
      });
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
         for (let index = 0; index < this.formulas.length; index++) {
            if (this.newFormula.formula_name.toLowerCase() === this.formulas[index].formula_name.toLowerCase()) {
              this.name_error = "name exists"
              return;
            }
          }
         this.$http.post('/api/formula/',this.newFormula)
           .then((response) => {
         $("#addFormulaModal").modal('hide');
         this.loading = false;
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
         this.error = err.bodyText;
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
         this.error = err.bodyText;
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
        var reader = new FileReader();
        reader.readAsText(this.formulaFile)
        reader.onload = (event)=> {
                this.csvData = event.target.result;
                console.log(this.csvData)
                $.post('/api/formula_import/', {'data':this.csvData}).done((response)=>{
                     this.loading = false;
                     this.csv_uploaded=true;
                     this.upload_errors = response['errors'].join('\n') + response['warnings'].join('\n')
                     this.getFormulas();
                 }).fail((err)=>{
                  this.upload_errors = err.responseText
                  this.loading = false;
                  console.log(err)
                })
        };
        reader.onerror = function() {
            alert('Unable to read ' + file.fileName);
        };
      },

      exportFormulaCSV: function() {
        // Export all current skus to a csv file
        // https://codepen.io/dimaZubkov/pen/eKGdxN
        // let csvContent = "data:text/csv;charset=utf-8,";
        // csvContent += [
        //   Object.keys(this.skus[0]).join(","),
        //   // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax
        //   ...this.skus.map(key => Object.values(key).join(","))
        // ].join("\n");

        this.$http.get('/api/formula_export/')
        .then((response) => {
          let csvContent = "data:text/csv;charset=utf-8,";
         let url = encodeURIComponent(response.data);
         url = csvContent + url;
         const link = document.createElement("a");
         link.setAttribute("href", url);
         link.setAttribute("download", "formula.csv");
         link.click();
        })
          .catch((err) => {
        this.loading = false;
        console.log(err);
        })        
      },

        sortBy: function(key) {
        this.sortKey = key
        this.sortAsc[key] = !this.sortAsc[key]
        if(!this.sortAsc[this.sortKey]){
          this.formulas = _.sortBy(this.formulas, this.sortKey)
        } else {
          this.formulas = _.sortBy(this.formulas, this.sortKey).reverse()
        }
      },
        disablePage: function(){
        this.disable_paginate = true;
      },
      
      onBlur: function(event) {
        if (event && this.search_term !== event.target.value) 
          this.search_term = event.target.value
      },
   
   },


  computed: {
    displayedFormulas () {
      var x = document.getElementById("pagination");
      if(this.disable_paginate){
          x.style.display = "none";
        return this.formulas;
      } else{
        x.style.display = "block";
         return this.paginate(this.formulas);
    }
    }
  },

   });