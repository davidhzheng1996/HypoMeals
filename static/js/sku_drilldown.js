// https://codesandbox.io/s/o29j95wx9
var global_items = {};
var vm = new Vue({
  el: '#starting',
  delimiters: ['${', '}'],
  data: {
    product_lines: [],
    customers: [],
    items:{},
    loading: false,
    message: null,
    selected_customer: '',
    page: 1,
    perPage: 10,
    pages: [],
    timespan: {'start_date':'','end_date':''},
    ingredientFile: null,
    chartData: [],
    search_term: '',
    search_input: '',
    request_dict: {},
    has_paginated: false,
    csv_uploaded: false,
    disable_paginate: false,
    // sorting variables
    // File Upload Errors
    upload_errors: '',
    name_error: '',
    error:'',
    unit_error: '',
  },
  mounted: function () {
    $("#search_input").autocomplete({
      minLength: 1,
      delay: 100,
      // https://stackoverflow.com/questions/9656523/jquery-autocomplete-with-callback-ajax-json
      source: function (request, response) {
        $.ajax({
          url: "/api/ingredient",
          dataType: "json",
          data: {
            // attach '?search=request.term' to the url 
            search: request.term
          },
          success: function (data) {
            ingr_names = $.map(data, function (item) {
              return [item.ingredient_name];
            })
            response(ingr_names);
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
    getItems: function (skuid) {
      // var span = this.updateTimespan();
      // console.log(span)
      this.loading = true;
      this.request_dict['timespan'] = this.timespan;
       this.request_dict['customer'] = this.selected_customer;
           this.$http.post('/api/get_sku_drilldown/'+skuid, this.request_dict)
               .then((response) => {
                   this.items = response.data;
                   global_items = this.items;
                   console.log(global_items)
                   for(key in this.items['rows']){
                    if(this.items['rows'].hasOwnProperty(key)){
                      var temp = [this.items['rows'][key].sale_date,this.items['rows'][key].revenue];
                      // console.log(temp)
                      this.chartData.push(temp);
                    }
                   }
                   // console.log(this.chartData)
                   this.loading = false;
               })
               .catch((err) => {
                   this.loading = false;
                   console.log(err);
               })
          this.$http.get('../api/customer')
            .then((response) => {
              this.customers = response.data;
              //this.getItems();
            })
            .catch((err) => {
                console.log(err);
            })
    },
      // getCustomer: function(){
      //   this.$http.get('../api/get_customer')
      //       .then((response) => {
      //         this.customers = response.data;
      //         //this.getItems();
      //       })
      //       .catch((err) => {
      //           console.log(err);
      //       })
      //   return;
      // },
      postCustomer: function(){
        // let api_url = 'api/customers/'
        // var e = document.getElementById("customers");
        // var text = e.options[e.selectedIndex].text;
        // let request = text;
        // this.$http.post(api_url, request)
        // .then((response) => {
        //   this.product_lines = response.data;
        // })
        // .catch((err) => {
        //     console.log(err);
        // })
      },
      getLineGraph: function(){

      },
      getSelected: function(event){
        this.selected_customer = event.target.value;
        this.getItems(savedSkuId);
      },
      updateTimespan: function(){
        $("#TimeSpanModal").modal('hide');
        this.getItems(savedSkuId);
      },
    // https://www.academind.com/learn/vue-js/snippets/image-upload/

    exportCSV: function() {
        this.loading = true;
        // Export all current skus to a csv file
        // https://codepen.io/dimaZubkov/pen/eKGdxN
        let csvContent = "data:text/csv;charset=utf-8,";
        // csvContent += [
        //   Object.keys(this.skus[0]).join(","),
        //   // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Spread_syntax
        //   ...this.skus.map(key => Object.values(key).join(","))
        // ].join("\n");
        for (key in this.items) {
            if (this.items.hasOwnProperty(key)) {
              if(key=='overall'){
                  let item_object = this.items[key];
                  csvContent += [["Entry", "Total Revenue","Avg Revenue/Case","Ingr Cost/Case","Avg Run Size","Avg Setup Cost/Case",
                  "Run Cost/Case","COGS/Case","Profit/Case","Profit Margin"].join(",") + '\n'];
                  csvContent += [['overall',item_object.revenue,item_object.avg_rev_per_case,item_object.ingr_cost_per_case,
                        item_object.avg_run_size,item_object.avg_setup_cost_per_case,item_object.run_cost_per_case,
                        item_object.cogs_per_case,item_object.profit_per_case,item_object.profit_margin].join(",")+'\n'];
              } else{
                csvContent+=[["Year","Week","Customer ID","Customer Name","Number of Sales","Price/case","Revenue"].join(",")+'\n'];
                let item_object = this.items[key];
                for(key in item_object){
                  if(item_object.hasOwnProperty(key)){
                    let row_object = item_object[key];
                        csvContent += [[row_object.year,row_object.week,row_object.customer_id,row_object.customer_name,
                        row_object.sales,row_object.price_per_case,row_object.revenue].join(",")+'\n']; 
                  }
                }
              }
            }
          }
        const url = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", "sku_drilldown.csv");
        link.click();
      },

    // Trigger an action to update search_term
    // Dirty trick to get around a VueJS bug: https://github.com/vuejs/vue/issues/5248 
    onBlur: function (event) {
      if (event && this.search_term !== event.target.value)
        this.search_term = event.target.value
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