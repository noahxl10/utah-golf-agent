import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TeeTimes } from './tee-times';

describe('TeeTimes', () => {
  let component: TeeTimes;
  let fixture: ComponentFixture<TeeTimes>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TeeTimes]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TeeTimes);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
