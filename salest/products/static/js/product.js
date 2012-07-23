$(document).ready(function(){
	
	$.fn.hasOneOfClasses = function(classes){
		var target = this
		var hasClass = false
		$(classes).each(function(index, el){
			if (target.hasClass(el)){
				hasClass = true
			}
		});
		return hasClass
	}
	
	var selectById = function(id, row){
		row = $(row)
		var selects = row.find('select')
		selects.each(function(index, el){
			el = $(el);
			el.val(el.find('option.' + id).attr('value'))
		})
	}
	var choosePhotos = function(prod_id){
		$('.photos .variation_photos').hide()
		$('.photos .'+ prod_id).show()
	}
	$(".products").each(function(index, el){
		el = $(el)
		var prod_id = $('.price-node span').first().attr('class').match(/variation_(\d+)/)[1]
		selectById(prod_id ,el)
		setPrice(el)
		choosePhotos(prod_id)
	})
	$('.variation_photos').each(function(index, el){
	// $(".group1").colorbox({rel:'group1'});
		el = $(el)
		el.find('a').colorbox({rel: el.attr('data_group')})
	})
	
	function setPrice(row){
		row = $(row)
		var selects = row.find('select')
		var select = selects.last()
		if (select.attr('disabled') == undefined){
			return
		}
		
		var ids = select.find(':selected').attr('class').split(' ')
		$(ids).each(function(index, v_id){
			var errors = false
			selects.each(function(index, el){
				if (!$(el).find(':selected').hasClass(v_id)){
					errors = true
					return
				}
			})
			if (!errors){
				var spans = $('.price-node span')
				spans.hide()
				spans.filter('.variation_' + v_id).show()
				choosePhotos(v_id)
				var link = $('.product-info a')
				link.attr('href', link.attr('href').replace(/\d+/, v_id))
				return
			}
		});
	}
	
	function getIds(selects, index){
		var toCheck = selects
		var ids = $(selects[0]).find(':selected').attr('class').split(' ')
		$(toCheck.slice(1, toCheck.length)).each(function(index, el){
			console.log(ids)
			var el = $(el)
			var selector = '.' + ids.join(' , .')
			el.find('option').hide()
			el.find(selector).show()
			if (!el.find(':selected').hasOneOfClasses(ids)){
				el.val(el.find(selector).first().attr('value'))
			}
			var localIds = $(el).find(':selected').attr('class').split(' ')
			$(ids).each(function(id_index, id_el){
				if(localIds.indexOf(id_el) == -1){
					ids.splice(ids.indexOf(id_el), 1)
				}
			})
		});
		return ids
		// console.log(toCheck)
		// var index = 
		
	}
	
	var rebuildChoices = function(select, selects, row){
		select = $(select)
		var index = selects.index(select)
		var ids = select.find(':selected').attr('class').split(' ')
		ids = getIds(selects, index)
		// var toRebuild = selects.slice(index + 1, selects.length)
		// var selector = '.' + ids.join(' , .')
		// toRebuild.find('option').hide()
		// toRebuild.find(selector).show()
		// toRebuild.each(function(index, select_el){
			// select_el = $(select_el)
			// if (!select_el.find(':selected').hasOneOfClasses(ids)){
				// select_el.val(select_el.find(selector).first().attr('value'))
			// }
		// })
	}
	
	$('.products select').bind('change', function(){
		var target = $(this)
		var row = target.parents('.products')
		var selects = row.find('select')
		var index = selects.index(this);
		rebuildChoices(target, selects, row)
		setPrice(row)
	});
})// end doc ready
