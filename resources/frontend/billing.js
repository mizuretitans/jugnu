const standardRates = [60000, 50000, 45000, 80000];
const durations = [30, 60, 90, 120];
const currency = new Intl.NumberFormat('en-IN', {style: 'currency', currency: 'INR', minimumFractionDigits: 0, maximumFractionDigits: 2});
const money = paise => currency.format(paise / 100);
const hourlyRate = mentor => get('rate.' + mentor, standardRates[mentor]);
const priceFor = (rate, minutes) => Math.round(rate * minutes / 60);

function bookingPage(mentor) {
  if (!mentors[mentor]) return page('Booking', 'Choose a mentor', links('mentors','Explore mentors'));
  if (!user) {
    sessionStorage.setItem('jugnu.next','book/' + mentor);
    return page('Session booking', 'Book with ' + mentors[mentor][0], '<div class="box narrow"><p>Log in as a student to choose your session length and review the price.</p>' + links('login','Student login') + '</div>');
  }
  if (user.role !== 'student') return dashboard();
  const rate = hourlyRate(mentor);
  return page('Session booking', 'Book with ' + mentors[mentor][0],
    '<form id="checkout" class="box narrow" data-mentor="'+mentor+'" data-rate="'+rate+'" data-id="'+crypto.randomUUID()+'"><span class="tag">Test checkout</span><h3>One-to-one teaching session</h3><p>'+money(rate)+' per hour</p><label>Session length<select name="minutes">'+durations.map(n=>'<option value="'+n+'" '+(n===60?'selected':'')+'>'+n+' minutes</option>').join('')+'</select></label><label>What would you like to learn?<textarea name="topic" required maxlength="300"></textarea></label><div class="bill-total">Session total <strong id="total" aria-live="polite">'+money(rate)+'</strong></div><p>This demo simulates payment. Your mentor can confirm the session, then you can agree on a time in messages.</p><p role="alert" id="checkout-error"></p><button>Pay with test funds</button></form>');
}

function sessionRows() {
  const records = Object.keys(localStorage).filter(k=>k.startsWith('jugnu.booking.'))
    .map(k=>JSON.parse(localStorage.getItem(k)))
    .filter(b=>user.role==='mentor' ? b.mentor===user.mentor : b.student===user.id)
    .sort((a,b)=>b.created-a.created);
  if (!records.length) return '<p>Your paid session bookings will appear here.</p>';
  return records.map(b=>{
    const isMentor=user.role==='mentor';
    let action='';
    if (isMentor && !b.confirmed) action='<button type="button" class="small" data-confirm-booking="'+b.id+'">Confirm session</button>';
    if (b.confirmed) action=links('messages/'+b.thread,'Message about this session','link');
    return '<article class="resource"><strong>'+esc(isMentor?b.name:mentors[b.mentor][0])+'</strong><p>'+esc(b.topic)+'</p><p>'+b.minutes+' minutes at '+money(b.rate)+'/hour · '+money(b.total)+' paid (test)</p><span class="tag">'+(b.confirmed?'Confirmed':'Awaiting mentor confirmation')+'</span><div>'+action+'</div></article>';
  }).join('');
}

function billingDashboard() {
  const rateForm=user.role==='mentor' ? '<form class="box" id="rate-form"><h3>Your teaching rate</h3><label>Hourly rate (₹)<input type="number" required name="rate" min="1" max="100000" step="1" value="'+hourlyRate(user.mentor)/100+'"></label><button class="small">Save hourly rate</button><p role="status" id="rate-status"></p></form>' : '';
  return '<div class="split billing"><div class="box"><h3>Paid sessions</h3>'+sessionRows()+'</div>'+rateForm+'</div>';
}

document.addEventListener('change',event=>{
  if(event.target.name!=='minutes') return;
  const form=event.target.form;
  document.querySelector('#total').textContent=money(priceFor(Number(form.dataset.rate),Number(event.target.value)));
});
document.addEventListener('submit',event=>{
  const form=event.target;
  if(form.id==='rate-form' && user?.role==='mentor'){
    event.preventDefault();
    const rate=Number(form.elements.rate.value);
    if(!Number.isInteger(rate)||rate<1||rate>100000)return;
    put('rate.'+user.mentor,rate*100);
    document.querySelector('#rate-status').textContent='Rate saved for new bookings.';
  }
  if(form.id!=='checkout'||user?.role!=='student')return;
  event.preventDefault();
  const {id}=form.dataset, mentor=Number(form.dataset.mentor), rate=hourlyRate(mentor);
  const minutes=Number(form.elements.minutes.value),topic=form.elements.topic.value.trim();
  if(!durations.includes(minutes)||!mentors[mentor])return;
  if(!topic){document.querySelector('#checkout-error').textContent='Enter a topic for your session.';return;}
  if(rate!==Number(form.dataset.rate)){
    render();
    document.querySelector('#checkout-error').textContent='The hourly rate changed. Please review the new total before paying.';
    return;
  }
  if(!get('booking.'+id,null))put('booking.'+id,{id,mentor,rate,minutes,topic,total:priceFor(rate,minutes),student:user.id,name:user.name,created:Date.now(),confirmed:false});
  go('dashboard');
});
document.addEventListener('click',event=>{
  const button=event.target.closest('[data-confirm-booking]');
  if(!button||user?.role!=='mentor')return;
  const b=get('booking.'+button.dataset.confirmBooking,null);
  if(!b||b.mentor!==user.mentor||b.confirmed)return;
  const requests=allReq();
  let thread=requests.find(r=>r.mentor===b.mentor&&r.student===b.student);
  if(!thread){thread={id:crypto.randomUUID(),mentor:b.mentor,student:b.student,name:b.name,messages:[]};requests.push(thread);}
  thread.status='Accepted';
  put('requests',requests);
  put('booking.'+b.id,{...b,confirmed:true,thread:thread.id});
  render();
});
