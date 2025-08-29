import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../environments/environment';

export interface TeeTime {
  start_time: string;
  date: string;
  course_name: string;
  holes: number[];
  provider: string;
  booking_url: string;
  is_available: boolean;
  green_fee: number;
  half_cart?: number;
  subtotal: number;
  price: number;
  restrictions?: string[];
  special_offer?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class TeeTimeService {

  
  private apiUrl = environment.apiUrl;
  private headers = new HttpHeaders({
    'Content-Type': 'application/json',
    // 'Authorization': 'Bearer ', // Example for an auth token
    // 'X-Custom-Header': ''  // Example for a custom header
  });

  constructor(private http: HttpClient) { }

  getAllTeeTimes(): Observable<TeeTime[]> {

    // 2. Pass the headers in the options object of the get method
    return this.http.get<TeeTime[]>(`${this.apiUrl}/test_api/teetimes`, { headers: this.headers });
  }

  getChronoGolfTeeTimes(): Observable<TeeTime[]> {
    return this.http.get<TeeTime[]>(`${this.apiUrl}/api/teetimes`, { headers: this.headers });
  }

  getForeUpTeeTimes(): Observable<TeeTime[]> {
    return this.http.get<TeeTime[]>(`${this.apiUrl}/api/foreup_teetimes`, { headers: this.headers });
  }

  getEaglewoodTeeTimes(): Observable<TeeTime[]> {
    return this.http.get<TeeTime[]>(`${this.apiUrl}/api/eaglewood_teetimes`, { headers: this.headers });
  }
}
