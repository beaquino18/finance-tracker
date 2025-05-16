
@main.route('/create_transaction', method=['GET', 'POST'])
@login_required
def create_transaction():
  form = TransactionForm()
  
  if form.validate_on_submit():
    new_transaction = Transaction(
      amount=form.amount.data,
      description=form.description.data,
      date=form.date.data,
      is_expense=form.is_expense.data,
      # TODO: category_id
      # TODO: wallet_id
      # TODO: labels
    )
    
    db.session.add(new_transaction)
    db.session.commit()
    
    flash('New Transaction created successfully')
    return redirect(url_for('main.transaction_detail.html', transaction_id=new_transaction.id))
  return render_template('create_transaction.html', form=form)

