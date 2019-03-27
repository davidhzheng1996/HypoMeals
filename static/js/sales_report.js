// https://codesandbox.io/s/o29j95wx9
new Vue({
  el: '#starting',
  delimiters: ['${', '}'],
  data: {
    items: [],
    product_lines: [],
    customers: [],
    skus: [],
    loading: false,
    currentIngredient: {},
    message: null,
    ingredientFile: null,
    search_term: '',
    search_input: '',
    has_paginated: false,
    csv_uploaded: false,
    disable_paginate: false,
    // sorting variables
    sortKey: 'ingredient_name',
    sortAsc: [
      {'id': true},
      { 'ingredient_name': true },
      { 'package_size': true },
      { 'cpp': true },
      { 'description': true },
      { 'id': true }
    ],
    // File Upload Errors
    upload_errors: '',
    name_error: '',
    error:'',
    unit_error: '',
    active_pls:[],
  },
  mounted: function () {
    this.getItems();
    // $("#search_input").autocomplete({
    //   minLength: 1,
    //   delay: 100,
    //   // https://stackoverflow.com/questions/9656523/jquery-autocomplete-with-callback-ajax-json
    //   source: function (request, response) {
    //     $.ajax({
    //       url: "/api/ingredient",
    //       dataType: "json",
    //       data: {
    //         // attach '?search=request.term' to the url 
    //         search: request.term
    //       },
    //       success: function (data) {
    //         ingr_names = $.map(data, function (item) {
    //           return [item.ingredient_name];
    //         })
    //         response(ingr_names);
    //       }
    //     });
    //   },
    //   messages: {
    //     noResults: '',
    //     results: function() {}
    //   }
    // });
  },
  methods: {
    getItems: function () {
      let api_url = '/api/sales_summary/';
           // https://medium.com/quick-code/searchfilter-using-django-and-vue-js-215af82e12cd
           // if(this.search_term !== '' && this.search_term !== null) {
           //      api_url = '/api/sku/?search=' + this.search_term;
           // }
           this.loading = true;
           //console.log(this.active_pls);
           this.$http.post(api_url, this.active_pls)
               .then((response) => {
                  // user selection status
                  this.items = response.data
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
    },
    getProductLines: function(){
      let api_url = '/api/product_line/';
           // https://medium.com/quick-code/searchfilter-using-django-and-vue-js-215af82e12cd
           this.loading = true;
           this.$http.get(api_url)
               .then((response) => {
                  this.product_lines = response.data;
                  this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
    },
    updateProductLines: function(event) {
      //let api_url = '/api/bulk_match_manufacturing_lines/';
        let actives = this.product_lines.filter((pl) => {
          return pl['all_active'];
        }).map((pl) => {
          return pl['product_line_name'];
        })
        $("#updatePLModal").modal('hide');
        // console.log(request)
        this.active_pls = actives;
        this.getItems();
      },
      postCustomer: function(){
        let api_url = 'api/customers/';
        var e = document.getElementById("customers");
        var text = e.options[e.selectedIndex].text;
        let request = text;
        this.$http.post(api_url, request)
        .then((response) => {
          
        })
        .catch((err) => {
            console.log(err);
        })
      },
      getCustomer: function(){
        let api_url = 'api/customers';
        this.$http.get(api_url)
        .then((response) => {
          this.customers = response.data;
        })
        .catch((err) => {
            console.log(err);
        })
      },
      viewDrilldown: function(skuid){
        window.location.href = '/sku_drilldown/'+skuid
      },
      pl_checkbox_click: function(ev, pl) {
        pl['all_active'] = true;
      },
      // disablePage: function(){
      //   this.disable_paginate = true;
      // },
   
      // ml_checkbox_click: function(ev, ml) {
      //   ml['part_active'] = false;
      // },
    // setPages: function () {
    //   let numberOfPages = Math.ceil(this.ingredients.length / this.perPage);
    //   for (let index = 1; index <= numberOfPages; index++) {
    //     this.pages.push(index);
    //   }
    // },
    // addPage: function () {
    //   this.pages.push(Math.ceil(this.ingredients.length / this.perPage) + 1);
    // },
    // deletePage: function () {
    //   this.pages = [];
    //   let numberOfPages = Math.ceil(this.ingredients.length / this.perPage);
    //   for (let index = 1; index < numberOfPages; index++) {
    //     this.pages.push(index);
    //   }
    // },
    // paginate: function (ingredients) {
    //   let page = this.page;
    //   // console.log(page)
    //   let perPage = this.perPage;
    //   let from = (page * perPage) - perPage;
    //   let to = (page * perPage);
    //   return ingredients.slice(from, to);
    // },
    // https://www.academind.com/learn/vue-js/snippets/image-upload/

    // exportCSV: function () {
      
    // },

    // Trigger an action to update search_term
    // Dirty trick to get around a VueJS bug: https://github.com/vuejs/vue/issues/5248 
    // onBlur: function (event) {
    //   if (event && this.search_term !== event.target.value)
    //     this.search_term = event.target.value
    // },

    getSkus: function (ingredientid) {
      this.loading = true;
      this.$http.get('/api/skus_to_ingredient/' + ingredientid)
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
    sortBy: function (key) {
      this.sortKey = key
      this.sortAsc[key] = !this.sortAsc[key]
      if (!this.sortAsc[this.sortKey]) {
        this.ingredients = _.sortBy(this.ingredients, this.sortKey)
      } else {
        this.ingredients = _.sortBy(this.ingredients, this.sortKey).reverse()
      }
    },

    // disablePage: function(){
    //     this.disable_paginate = true;
    //   },

  },

  // computed: {
  //   // is pagination necessary though?
  //   displayedIngredients() {
  //     var x = document.getElementById("pagination");
  //     if(this.disable_paginate){
  //         x.style.display = "none";
  //       return this.ingredients;
  //     } else{
  //       x.style.display = "block";
  //        return this.paginate(this.ingredients);
  //   }
  //   }
  // },


});