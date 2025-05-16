@main.route('/create_category', method=['GET', 'POST'])
@login_required
def create_category():
  form = CategoryForm
  
  if form.validate_on_submit():
    new_category = Category(
      name=form.name.data,
      color=form.color.data,
      icon=form.icon.data
    )
    
    db.session.add(new_category)
    db.session.commit()
    
    flash('New category created successfully')
    return redirect(url_for('main.category_detail', category_id=new_category.id))
  return render_template('create_category.html', form=form)
