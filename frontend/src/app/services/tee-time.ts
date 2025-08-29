import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface TeeTime {
  start_time: string;
  date: string;
  course_name: string;
  holes: number[];
  provider: string;
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
  private apiUrl = 'https://10b7ea48-718e-4018-b4c6-704734d94440-00-1i3wtbxx6pimv.worf.replit.dev:8000';

  constructor(private http: HttpClient) { }

  getAllTeeTimes(): Observable<TeeTime[]> {
    return this.http.get<TeeTime[]>(`${this.apiUrl}/test_api/teetimes`);
  }

  getChronoGolfTeeTimes(): Observable<TeeTime[]> {
    return this.http.get<TeeTime[]>(`${this.apiUrl}/api/teetimes`);
  }

  getForeUpTeeTimes(): Observable<TeeTime[]> {
    return this.http.get<TeeTime[]>(`${this.apiUrl}/api/foreup_teetimes`);
  }

  getEaglewoodTeeTimes(): Observable<TeeTime[]> {
    return this.http.get<TeeTime[]>(`${this.apiUrl}/api/eaglewood_teetimes`);
  }
}
