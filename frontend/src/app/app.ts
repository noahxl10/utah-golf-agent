import { Component } from '@angular/core';
import { TeeTimes } from './tee-times/tee-times';

@Component({
  selector: 'app-root',
  imports: [TeeTimes],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  title = 'Utah Golf Booking';
}
