// https://codesandbox.io/s/o29j95wx9
new Vue({
  el: '#starting',
  delimiters: ['${', '}'],
  data: {
    items: [],
    product_lines: [],
    customers: [],
    loading: false,
    message: null,
    ingredientFile: null,
    search_term: '',
    search_input: '',
    has_paginated: false,
    csv_uploaded: false,
    disable_paginate: false,
    selected_customer:'',
    request_dict:{},
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
           this.request_dict['pl'] = this.active_pls;
           this.request_dict['customer'] = this.selected_customer;
           console.log(this.request_dict)
           this.$http.post(api_url, this.request_dict)
               .then((response) => {
                  // user selection status
                  this.items = response.data
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
            this.$http.get('api/customer')
            .then((response) => {
              this.customers = response.data;
              //console.log(this.customers)
              //this.getItems();
            })
            .catch((err) => {
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
        // let api_url = 'api/customer/';
        // var e = document.getElementById("customers");
        // var text = e.options[e.selectedIndex].text;
        // let request = text;
        // this.$http.post(api_url, request)
        // .then((response) => {
          
        // })
        // .catch((err) => {
        //     console.log(err);
        // })
      },
      // getCustomer: function(){
      //   let api_url = 'api/customer';
      //   this.$http.get(api_url)
      //   .then((response) => {
      //     this.customers = response.data;
      //     //console.log(this.customers)
      //     //this.getItems();
      //   })
      //   .catch((err) => {
      //       console.log(err);
      //   })
      // },
      getSelected: function(event){
        this.selected_customer = event.target.value;
        this.getItems();
      },
      viewDrilldown: function(skuid){
        window.location.href = '/sku_drilldown/'+skuid
      },
      pl_checkbox_click: function(ev, pl) {
        pl['all_active'] = true;
      },

      exportSkuCSV: function() {
        this.loading = true;
        // Export all current skus to a csv file
        // https://codepen.io/dimaZubkov/pen/eKGdxN
        let csvContent = "data:text/csv;charset=utf-8,";
        csvContent += [
          Object.keys(this.skus[0]).join(","),
          // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax
          ...this.skus.map(key => Object.values(key).join(","))
        ].join("\n");
        const url = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "sales_report.csv");
        link.click();
      },

    // Trigger an action to update search_term
    // Dirty trick to get around a VueJS bug: https://github.com/vuejs/vue/issues/5248 
    // onBlur: function (event) {
    //   if (event && this.search_term !== event.target.value)
    //     this.search_term = event.target.value
    // },



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