var vm = new Vue({
     el: '#starting',
     delimiters: ['${','}'],
     data: {
     skus: [],
     loading: false,
     //currentSku: {},
     message: null,
     page:1,
     perPage: 10,
     pages:[],
     has_paginated:false,
     //COUPLED WITH BACKEND DO NOT REMOVE BELOW
     //newSku: { 'ingredient_name': '', 'quantity':0 },
   },
   mounted: function() {},
   methods: {
       getSkus: function(ingredientid){
           this.loading = true;
           this.$http.get('/api/skus_to_ingredient/'+ingredientid)
               .then((response) => {
                   this.skus = response.data;
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
       setPages: function () {
        let numberOfPages = Math.ceil(this.skus.length / this.perPage);
        for (let index = 1; index <= numberOfPages; index++) {
          this.pages.push(index);
        }
      },
    paginate: function (skus) {
      let page = this.page;
      let perPage = this.perPage;
      let from = (page * perPage) - perPage;
      let to = (page * perPage);
      return  skus.slice(from, to);
    },
   },
   computed: {
    displayedSkus () {
      return this.paginate(this.skus);
    }
  },
   });