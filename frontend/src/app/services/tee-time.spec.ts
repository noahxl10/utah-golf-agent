import { TestBed } from '@angular/core/testing';

import { TeeTime } from './tee-time';

describe('TeeTime', () => {
  let service: TeeTime;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TeeTime);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
