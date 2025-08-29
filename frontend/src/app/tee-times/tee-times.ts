import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TeeTimeService, TeeTime } from '../services/tee-time';

@Component({
  selector: 'app-tee-times',
  imports: [CommonModule],
  templateUrl: './tee-times.html',
  styleUrl: './tee-times.css'
})
export class TeeTimes implements OnInit {
  teeTimes: TeeTime[] = [];
  loading = false;
  error = '';

  constructor(private teeTimeService: TeeTimeService) { }

  ngOnInit(): void {
    this.loadTestTeeTimes();
  }

  loadTestTeeTimes() {
    this.loading = true;
    this.error = '';
    this.teeTimeService.getAllTeeTimes().subscribe({
      next: (data) => {
        this.teeTimes = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load tee times';
        this.loading = false;
        console.error('Error loading tee times:', err);
      }
    });
  }

  loadChronoGolfTeeTimes() {
    this.loading = true;
    this.error = '';
    this.teeTimeService.getChronoGolfTeeTimes().subscribe({
      next: (data) => {
        this.teeTimes = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load ChronoGolf tee times';
        this.loading = false;
        console.error('Error loading ChronoGolf tee times:', err);
      }
    });
  }

  loadForeUpTeeTimes() {
    this.loading = true;
    this.error = '';
    this.teeTimeService.getForeUpTeeTimes().subscribe({
      next: (data) => {
        this.teeTimes = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load ForeUp tee times';
        this.loading = false;
        console.error('Error loading ForeUp tee times:', err);
      }
    });
  }

  loadEaglewoodTeeTimes() {
    this.loading = true;
    this.error = '';
    this.teeTimeService.getEaglewoodTeeTimes().subscribe({
      next: (data) => {
        this.teeTimes = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load Eaglewood tee times';
        this.loading = false;
        console.error('Error loading Eaglewood tee times:', err);
      }
    });
  }
}
