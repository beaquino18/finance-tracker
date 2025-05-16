@main.route('/create_label', method=['GET', 'POST'])
@login_required
def create_label():
  form = LabelForm()
  
  if form.validate_on_submit():
    new_label = Label(
      name=form.name.data
    )
    
    db.session.add(new_label)
    db.session.commit()
    
    flash('New label created successfully')
    return redirect(url_for('main.label_detail', label_id=new_label.id))
  return render_template('create_label.html', form=form)

