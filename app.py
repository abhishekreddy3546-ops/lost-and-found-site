@app.route('/report-lost', methods=['POST'])
def submit_lost():
    new_item = TrackedItem(
        name=request.form.get('lostName'),
        category=request.form.get('lostCategory'),
        status='lost',
        description=request.form.get('lostDesc'),
        location=request.form.get('lostLoc'),
        date=request.form.get('lostDate'),
        contact=request.form.get('lostContact')
    )
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/report-found', methods=['POST'])
def submit_found():
    new_item = TrackedItem(
        name=request.form.get('foundName'),
        category=request.form.get('foundCategory'),
        status='found',
        description=request.form.get('foundDesc'),
        location=request.form.get('foundLoc'),
        date=request.form.get('foundDate'),
        contact=request.form.get('foundContact')
    )
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('index'))
